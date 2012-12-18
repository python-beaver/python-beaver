import errno
import os
import platform
import stat
import sys
import time

from ssh_tunnel import BeaverSshTunnel
from transport import TransportException
from utils import eglob

REOPEN_FILES = 'linux' not in platform.platform().lower()


class Worker(object):
    """Looks for changes in all files of a directory.
    This is useful for watching log file changes in real-time.
    It also supports files rotation.

    Example:

    >>> def callback(filename, lines):
    ...     print filename, lines
    ...
    >>> l = Worker(args, callback, ["log", "txt"], tail_lines=0)
    >>> l.loop()
    """

    def __init__(self, file_config, beaver_config, callback, logger, ssh_tunnel=None, extensions=["log"], tail_lines=0):
        """Arguments:

        (FileConfig) @file_config:
            object containing file-related configuration

        (BeaverConfig) @beaver_config:
            object containing global configuration

        (callable) @callback:
            a function which is called every time a new line in a
            file being watched is found;
            this is called with "filename" and "lines" arguments.

        (list) @extensions:
            only watch files with these extensions

        (int) @tail_lines:
            read last N lines from files being watched before starting
        """
        self.beaver_config = beaver_config
        self.file_config = file_config
        self.callback = callback
        self.extensions = extensions
        self.files_map = {}
        self._logger = logger

        if self.beaver_config.get('path') is not None:
            self.folder = os.path.realpath(self.beaver_config.get('path'))
            assert os.path.isdir(self.folder), "%s does not exists" \
                                            % self.folder
        assert callable(callback)
        self.update_files()
        # The first time we run the script we move all file markers at EOF.
        # In case of files created afterwards we don't do this.
        for id, file in self.files_map.iteritems():
            file.seek(os.path.getsize(file.name))  # EOF
            if tail_lines:
                lines = self.tail(file.name, tail_lines)
                if lines:
                    self.callback(file.name, lines)

    def __del__(self):
        self.close()

    def loop(self, interval=0.1, async=False):
        """Start the loop.
        If async is True make one loop then return.
        """
        while 1:
            self.update_files()
            for fid, file in list(self.files_map.iteritems()):
                try:
                    self.readfile(fid, file)
                except IOError, e:
                    if e.errno == errno.ESTALE:
                        self.unwatch(file, fid)
            if async:
                return
            time.sleep(interval)

    def listdir(self):
        """List directory and filter files by extension.
        You may want to override this to add extra logic or
        globbling support.
        """
        ls = os.listdir(self.folder)
        if self.extensions:
            return [x for x in ls if os.path.splitext(x)[1][1:] \
                                           in self.extensions]
        else:
            return ls

    @staticmethod
    def tail(fname, window):
        """Read last N lines from file fname."""
        try:
            f = open(fname, 'r')
        except IOError, err:
            if err.errno == errno.ENOENT:
                return []
            else:
                raise
        else:
            BUFSIZ = 1024
            f.seek(0, os.SEEK_END)
            fsize = f.tell()
            block = -1
            data = ""
            exit = False
            while not exit:
                step = (block * BUFSIZ)
                if abs(step) >= fsize:
                    f.seek(0)
                    exit = True
                else:
                    f.seek(step, os.SEEK_END)
                data = f.read().strip()
                if data.count('\n') >= window:
                    break
                else:
                    block -= 1
            return data.splitlines()[-window:]

    def update_files(self):
        ls = []
        files = []
        if len(self.beaver_config.get('globs')) > 0:
            for name in self.beaver_config.get('globs'):
                globbed = [os.path.realpath(filename) for filename in eglob(name)]
                files.extend(globbed)
                self.file_config.addglob(name, globbed)
        else:
            for name in self.listdir():
                files.append(os.path.realpath(os.path.join(self.folder, name)))

        for absname in files:
            try:
                st = os.stat(absname)
            except EnvironmentError, err:
                if err.errno != errno.ENOENT:
                    raise
            else:
                if not stat.S_ISREG(st.st_mode):
                    continue
                fid = self.get_file_id(st)
                ls.append((fid, absname))

        # check existent files
        for fid, file in list(self.files_map.iteritems()):
            try:
                st = os.stat(file.name)
            except EnvironmentError, err:
                if err.errno == errno.ENOENT:
                    self.unwatch(file, fid)
                else:
                    raise
            else:
                if fid != self.get_file_id(st):
                    # same name but different file (rotation); reload it.
                    self._logger.info("[{0}] - file rotated {1}".format(fid, file.name))
                    self.unwatch(file, fid)
                    self.watch(file.name)
                elif file.tell() > st.st_size:
                    # file truncated; reload it
                    self._logger.info("[{0}] - file truncated {1}".format(fid, file.name))
                    self.unwatch(file, fid)
                    self.watch(file.name)
                elif REOPEN_FILES:
                    self._logger.debug("[{0}] - file reloaded (non-linux) {1}".format(fid, file.name))
                    position = file.tell()
                    fname = file.name
                    file.close()
                    file = open(fname, "r")
                    file.seek(position)
                    self.files_map[fid] = file

        # add new ones
        for fid, fname in ls:
            if fid not in self.files_map:
                self.watch(fname)

    def readfile(self, fid, file):
        lines = file.readlines()
        if lines:
            self.callback(file.name, lines)

    def watch(self, fname):
        try:
            file = open(fname, "r")
            fid = self.get_file_id(os.stat(fname))
        except EnvironmentError, err:
            if err.errno != errno.ENOENT:
                raise
        else:
            self._logger.info("[{0}] - watching logfile {1}".format(fid, fname))
            self.files_map[fid] = file

    def unwatch(self, file, fid):
        # file no longer exists; if it has been renamed
        # try to read it for the last time in case the
        # log rotator has written something in it.
        lines = None
        try:
            lines = self.readfile(fid, file)
        except IOError:
            # Silently ignore any IOErrors -- file is gone
            pass
        self._logger.info("[{0}] - un-watching logfile {1}".format(fid, file.name))
        del self.files_map[fid]
        if lines:
            self.callback(file.name, lines)

    @staticmethod
    def get_file_id(st):
        return "%xg%x" % (st.st_dev, st.st_ino)

    def close(self):
        for id, file in self.files_map.iteritems():
            file.close()
        self.files_map.clear()


def create_transport(file_config, beaver_config):
    if beaver_config.get('transport') == 'rabbitmq':
        import beaver.rabbitmq_transport
        transport = beaver.rabbitmq_transport.RabbitmqTransport(file_config, beaver_config)
    elif beaver_config.get('transport') == 'redis':
        import beaver.redis_transport
        transport = beaver.redis_transport.RedisTransport(file_config, beaver_config)
    elif beaver_config.get('transport') == 'stdout':
        import beaver.stdout_transport
        transport = beaver.stdout_transport.StdoutTransport(file_config, beaver_config)
    elif beaver_config.get('transport') == 'udp':
        import beaver.udp_transport
        transport = beaver.udp_transport.UdpTransport(file_config, beaver_config)
    elif beaver_config.get('transport') == 'zmq':
        import beaver.zmq_transport
        transport = beaver.zmq_transport.ZmqTransport(file_config, beaver_config)
    else:
        raise Exception('Invalid transport {0}'.format(beaver_config.get('transport')))

    return transport


def create_ssh_tunnel(file_config, beaver_config):
    if not beaver_config.use_ssh_tunnel():
        return None

    return BeaverSshTunnel(beaver_config)


def run_worker(file_config, beaver_config, logger, ssh_tunnel=None):
    logger.info("Logging using the {0} transport".format(beaver_config.get('transport')))
    transport = create_transport(file_config, beaver_config)

    if REOPEN_FILES:
        logger.info("Detected non-linux platform. Files will be reopened for tailing")

    try:
        logger.info("Starting worker...")
        l = Worker(file_config, beaver_config, transport.callback, logger, ssh_tunnel=ssh_tunnel)
        logger.info("Working...")
        l.loop()
    except TransportException, e:
        raise TransportException(e.message)
    except KeyboardInterrupt:
        logger.info("Shutting down. Please wait.")
        transport.interrupt()
        logger.info("Shutdown complete.")
        sys.exit(0)
    except Exception:
        import traceback
        exception_list = traceback.format_stack()
        exception_list = exception_list[:-2]
        exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
        exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))
        exception_str = "Traceback (most recent call last):\n"
        exception_str += "".join(exception_list)
        exception_str = exception_str[:-1]

        logger.info("Unhandled Exception:")
        logger.info(exception_str)

        transport.unhandled()
        sys.exit(1)
