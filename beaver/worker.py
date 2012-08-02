import datetime
import errno
import os
import stat
import sys
import time
import beaver.transports as transports


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

    def __init__(self, args, callback, extensions=["log"], tail_lines=0):
        """Arguments:

        (str) @args:
            set of arguments for the worker

        (callable) @callback:
            a function which is called every time a new line in a
            file being watched is found;
            this is called with "filename" and "lines" arguments.

        (list) @extensions:
            only watch files with these extensions

        (int) @tail_lines:
            read last N lines from files being watched before starting
        """
        self.files_map = {}
        self.callback = callback
        self.extensions = extensions
        self.config = args

        if self.config.path is not None:
            self.folder = os.path.realpath(args.path)
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
                self.readfile(file)
            if async:
                return
            time.sleep(interval)

    def log(self, line):
        """Log when a file is un/watched"""
        print "[{0}] {1}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'), line)

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
        if self.config.files is not None:
            for name in self.config.files:
                files.append(os.path.realpath(name))
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
                    self.unwatch(file, fid)
                    self.watch(file.name)

        # add new ones
        for fid, fname in ls:
            if fid not in self.files_map:
                self.watch(fname)

    def readfile(self, file):
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
            self.log("[{0}] - watching logfile {1}".format(fid, fname))
            self.files_map[fid] = file

    def unwatch(self, file, fid):
        # file no longer exists; if it has been renamed
        # try to read it for the last time in case the
        # log rotator has written something in it.
        lines = self.readfile(file)
        self.log("[{0}] - un-watching logfile {1}".format(fid, file.name))
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


def run_worker(options):
    if options.transport not in ['zmq', 'redis', 'stdout']:
        raise Exception('Invalid transport {0}'.format(options.transport))

    if options.transport == 'zmq':
        transport = transports.ZmqTransport()
    if options.transport == 'redis':
        transport = transports.RedisTransport()
    if options.transport == 'stdout':
        transport = transports.StdoutTransport()

    try:
        print "[{0}] Starting worker...".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'))
        l = Worker(options, transport.callback)
        print "[{0}] Working...".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'))
        l.loop()
    except KeyboardInterrupt:
        print "\n[{0}] Shutting down. Please wait.".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'))
        transport.interrupt()
        print "[{0}] Shutdown complete.".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'))
        sys.exit(0)
    except Exception, e:
        print "[{0}] Unhandled Exception: {1}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%i:%s'), str(e))
        transport.unhandled()
        sys.exit(1)
