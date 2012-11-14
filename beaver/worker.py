import errno
import glob
import logging
import os
import stat
import sys
import time
import hashlib
import gzip
import re


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

    def __init__(self, args, configfile, callback, extensions=["log"], tail_lines=0):
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
        self.logger = logging.getLogger('beaver')
        self.config = args
        self.configfile = configfile
        self.sincedb_prefix = ".sincedb-"
        self.sincedb_lut = {}
        self.tail_lines = tail_lines

        if self.config.path is not None:
            self.folder = os.path.realpath(args.path)
            assert os.path.isdir(self.folder), "%s does not exists" \
                                            % self.folder
        assert callable(callback)
        self.update_files()
        # The first time we run the script we move all file markers at EOF.
        # In case of files created afterwards we don't do this.
        for id, file in self.files_map.iteritems():
            # If sincedb_path is defined, don't seek to the end of the file,
            # and ignore the value of tail_lines.  Unless start_position is tail
            # then tail is handled by init_sincedb and watch
            if not self.configfile._getfield(file.name, "sincedb_path"):
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

    # Pass in a filename, a hash of the first line of the file, and an override starting line
    # Populates an internal hash of filesnames to sincedb info
    # Returns the offset line to start with
    def init_sincedb(self, filename, sincedb_hash, line=0):
        # Open the file ~/.sincedb-${sincedb_hash} if it exists
        sincedb_path = self.configfile._getfield(filename, "sincedb_path")
        try:
          f = open(sincedb_path + "/" + self.sincedb_prefix + sincedb_hash, 'r')
        except IOError, err:
            # We only care if it's not a non-existant file error
            if err.errno != errno.ENOENT:
                raise
            else: # Sincedb file doesn't exist, where shall we start?
                start_position = self.configfile._getfield(filename, "start_position")
                if start_position == "beginning":
                    line=0
                elif start_position == "end":
                    line=-1
                elif start_position == "tail":
                    if self.tail_lines==0:
                        line=-1
                    else:
                        line=-1*self.tail_lines
        else:
          # There should only be one line containing the last read line offset
          data = f.readline()
          values=data.split("\t")
          if not values:
              line = 0
          else:
              try:
                  line = int(values[0])
              except ValueError:
                  line = 0
          f.close()
        
        # Populate self.sincedb_lut with the info
	self.sincedb_lut[filename]={'hash': sincedb_hash, 'line': line}
        return line

    def update_sincedb(self, filename, lines_read):
        sincedb_hash = self.sincedb_lut[filename]['hash']
        lines = self.sincedb_lut[filename]['line'] + lines_read
        self.sincedb_lut[filename]['line'] = lines
        sincedb_path = self.configfile._getfield(filename, "sincedb_path")
        try:
          f = open(sincedb_path + "/" + self.sincedb_prefix + sincedb_hash, 'w')
        except IOError, err:
            # We only care if it's not a non-existant file error
            if err.errno != errno.ENOENT:
                raise
        else:
          # There should only be one line containing the last read line offset
          f.write(str(lines)+"\t"+filename+"\n")
          f.close()
        return True

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
        if len(self.config.files) > 0:
            for name in self.config.files:
                files.extend([os.path.realpath(globbed) for globbed in glob.glob(name)])
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
        again = True
        while again:
            lines = file.readlines(102400)
            if lines:
                self.callback(file.name, lines)
                self.update_sincedb(file.name, len(lines))
            else:
                again=False

    def file_len(file):
        # Make sure to start at the top
        file.seek(0, os.SEEK_SET)
        lines = 0
        buf_size = 1024 * 1024
        read_f = file.read # loop optimization

        buf = read_f(buf_size)
        while buf:
            lines += buf.count('\n')
            buf = read_f(buf_size)

        # Reset to the top
        file.seek(0, os.SEEK_SET)
        return lines

    def watch(self, fname):
        try:
            if re.search('.gz$', fname):
                file = gzip.open(fname, "rb")
            else:
                file = open(fname, "r")
            fid = self.get_file_id(os.stat(fname))
            if self.configfile._getfield(fname, "sincedb_path"):
                # Read the first line
                file.seek(0, os.SEEK_SET)
                first_line = file.readline()
                file.seek(0, os.SEEK_SET)
                if first_line:
                    # Generate a hash from that line
                    sincedb_hash = hashlib.sha1(first_line).hexdigest()
                    # Init sincedb
                    starting_line = self.init_sincedb(fname, sincedb_hash)
                    if starting_line < 0:
                        # Figure out how long the file is, and translate to a positive number
                        starting_line = self.file_len(file)+starting_line
                    # Seek to the relevant line
                    current_line=0
                    while current_line < starting_line:
                        file.readline()
                        current_line+=1
                    
        except EnvironmentError, err:
            if err.errno != errno.ENOENT:
                raise
        else:
            self.logger.info("[{0}] - watching logfile {1}".format(fid, fname))
            self.files_map[fid] = file

    def unwatch(self, file, fid):
        # file no longer exists; if it has been renamed
        # try to read it for the last time in case the
        # log rotator has written something in it.
        lines = self.readfile(file)
        self.logger.info("[{0}] - un-watching logfile {1}".format(fid, file.name))
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


def run_worker(options, fileconfig):
    logger = logging.getLogger('beaver')
    logger.info("Logging using the {0} transport".format(options.transport))

    if options.transport == 'redis':
        import beaver.redis_transport
        transport = beaver.redis_transport.RedisTransport(fileconfig)
    elif options.transport == 'stdout':
        import beaver.stdout_transport
        transport = beaver.stdout_transport.StdoutTransport(fileconfig)
    elif options.transport == 'zmq':
        import beaver.zmq_transport
        transport = beaver.zmq_transport.ZmqTransport(fileconfig)
    elif options.transport == 'rabbitmq':
        import beaver.rabbitmq_transport
        transport = beaver.rabbitmq_transport.RabbitmqTransport(fileconfig)
    elif options.transport == 'udp':
        import beaver.udp_transport
        transport = beaver.udp_transport.UdpTransport(fileconfig)
    else:
        raise Exception('Invalid transport {0}'.format(options.transport))


    try:
        logger.info("Starting worker...")
        l = Worker(options, fileconfig, transport.callback)
        logger.info("Working...")
        l.loop()
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
