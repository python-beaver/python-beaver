# -*- coding: utf-8 -*-
import datetime
import errno
import gzip
import io
import os
import sqlite3
import stat
import time

from beaver.utils import IS_GZIPPED_FILE, REOPEN_FILES, eglob
from beaver.unicode_dammit import ENCODINGS


class Worker(object):
    """Looks for changes in all files of a directory.
    This is useful for watching log file changes in real-time.
    It also supports files rotation.

    Example:

    >>> def callback(filename, lines):
    ...     print filename, lines
    ...
    >>> l = Worker(args, callback, ["log", "txt"])
    >>> l.loop()
    """

    def __init__(self, beaver_config, file_config, queue_consumer_function, callback, logger=None):
        """Arguments:

        (FileConfig) @file_config:
            object containing file-related configuration

        (BeaverConfig) @beaver_config:
            object containing global configuration

        (Logger) @logger
            object containing a python logger

        (callable) @callback:
            a function which is called every time a new line in a
            file being watched is found;
            this is called with "filename" and "lines" arguments.
        """
        self._beaver_config = beaver_config
        self._callback = callback
        self._create_queue_consumer = queue_consumer_function
        self._file_config = file_config
        self._file_map = {}
        self._folder = self._beaver_config.get('path')
        self._logger = logger
        self._proc = None
        self._sincedb_path = self._beaver_config.get('sincedb_path')
        self._update_time = None

        if not callable(self._callback):
            raise RuntimeError("Callback for worker is not callable")

        self.update_files()
        self.seek_to_end()

    def __del__(self):
        """Closes all files"""
        self.close()

    def close(self):
        """Closes all currently open file pointers"""
        for id, data in self._file_map.iteritems():
            data['file'].close()
        self._file_map.clear()

    def listdir(self):
        """List directory and filter files by extension.
        You may want to override this to add extra logic or
        globbling support.
        """
        ls = os.listdir(self._folder)
        return [x for x in ls if os.path.splitext(x)[1][1:] == "log"]

    def loop(self, interval=0.1, async=False):
        """Start the loop.
        If async is True make one loop then return.
        """
        while True:
            t = time.time()
            if not (self._proc and self._proc.is_alive()):
                self._proc = self._create_queue_consumer()

            if int(time.time()) - self._update_time > self._beaver_config.get('discover_interval'):
                self.update_files()

            for fid, data in self._file_map.iteritems():
                try:
                    self.readfile(fid, data['file'])
                except IOError, e:
                    if e.errno == errno.ESTALE:
                        self.unwatch(data['file'], fid)
            if async:
                return

            self._logger.debug("Iteration took {0:.6f}".format(time.time() - t))
            time.sleep(interval)

    def readfile(self, fid, file):
        """Read lines from a file and performs a callback against them"""
        lines = file.readlines(4096)
        line_count = 0
        while lines:
            if self._sincedb_path:
                current_line_count = len(lines)
                if not self._sincedb_update_position(file, fid=fid, lines=current_line_count):
                    line_count += current_line_count

            self._callback(("callback", {
                'filename': file.name,
                'lines': lines,
                'timestamp': datetime.datetime.utcnow().isoformat() + "Z",
            }))

            lines = file.readlines(4096)

        if line_count > 0:
            self._sincedb_update_position(file, fid=fid, lines=line_count, force_update=True)

    def seek_to_end(self):
        # The first time we run the script we move all file markers at EOF.
        # In case of files created afterwards we don't do this.
        for fid, data in self._file_map.iteritems():
            self._logger.debug("[{0}] - getting start position {1}".format(fid, data['file'].name))
            start_position = self._file_config.get('start_position', data['file'].name)

            if self._sincedb_path:
                sincedb_start_position = self._sincedb_start_position(data['file'], fid=fid)
                if sincedb_start_position:
                    start_position = sincedb_start_position

            if start_position == "beginning":
                continue

            line_count = 0

            if str(start_position).isdigit():
                self._logger.debug("[{0}] - going to start position {1} for {2}".format(fid, start_position, data['file'].name))
                start_position = int(start_position)
                for encoding in ENCODINGS:
                    try:
                        line_count = 0
                        while data['file'].readline():
                            line_count += 1
                            if line_count == start_position:
                                break
                    except UnicodeDecodeError:
                        self._logger.debug("[{0}] - UnicodeDecodeError raised for {1} with encoding {2}".format(fid, data['file'].name, data['encoding']))
                        data['file'] = self.open(data['file'].name, encoding=encoding)
                        data['encoding'] = encoding

                    if line_count != start_position:
                        self._logger.debug("[{0}] - file at different position than {1}, assuming manual truncate for {2}".format(fid, start_position, data['file'].name))
                        data['file'].seek(0, os.SEEK_SET)
                        start_position == "beginning"

            if start_position == "beginning":
                continue

            if start_position == "end":
                self._logger.debug("[{0}] - getting end position for {1}".format(fid, data['file'].name))
                for encoding in ENCODINGS:
                    try:
                        line_count = 0
                        while data['file'].readline():
                            line_count += 1
                        break
                    except UnicodeDecodeError:
                        self._logger.debug("[{0}] - UnicodeDecodeError raised for {1} with encoding {2}".format(fid, data['file'].name, data['encoding']))
                        data['file'] = self.open(data['file'].name, encoding=encoding)
                        data['encoding'] = encoding

            current_position = data['file'].tell()
            self._logger.debug("[{0}] - line count {1} for {2}".format(fid, line_count, data['file'].name))
            self._sincedb_update_position(data['file'], fid=fid, lines=line_count, force_update=True)

            tail_lines = self._file_config.get('tail_lines', data['file'].name)
            tail_lines = int(tail_lines)
            if tail_lines:
                encoding = data['encoding']

                lines = self.tail(data['file'].name, encoding=encoding, window=tail_lines, position=current_position)
                if lines:
                    self._callback(("callback", {
                        'filename': data['file'].name,
                        'lines': lines,
                        'timestamp': datetime.datetime.utcnow().isoformat() + "Z",
                    }))

    def _sincedb_init(self):
        """Initializes the sincedb schema in an sqlite db"""
        if not self._sincedb_path:
            return

        if not os.path.exists(self._sincedb_path):
            self._logger.debug('Initializing sincedb sqlite schema')
            conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
            conn.execute("""
            create table sincedb (
                fid      text primary key,
                filename text,
                position integer default 1
            );
            """)
            conn.close()

    def _sincedb_update_position(self, file, fid=None, lines=0, force_update=False):
        """Retrieves the starting position from the sincedb sql db for a given file
        Returns a boolean representing whether or not it updated the record
        """
        if not self._sincedb_path:
            return False

        if not fid:
            fid = self.get_file_id(os.stat(file.name))

        current_time = int(time.time())
        update_time = self._file_map[fid]['update_time']
        if not force_update:
            sincedb_write_interval = self._file_config.get('sincedb_write_interval', file.name)
            if update_time and current_time - update_time <= sincedb_write_interval:
                return False

            if lines == 0:
                return False

        self._sincedb_init()

        old_count = self._file_map[fid]['line']
        self._file_map[fid]['update_time'] = current_time
        self._file_map[fid]['line'] = old_count + lines
        lines = self._file_map[fid]['line']

        self._logger.debug("[{0}] - updating sincedb for logfile {1} from {2} to {3}".format(fid, file.name, old_count, lines))

        conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
        cursor = conn.cursor()
        query = "insert or ignore into sincedb (fid, filename) values (:fid, :filename);"
        cursor.execute(query, {
            'fid': fid,
            'filename': file.name
        })

        query = "update sincedb set position = :position where fid = :fid and filename = :filename"
        cursor.execute(query, {
            'fid': fid,
            'filename': file.name,
            'position': int(lines),
        })
        conn.close()

        return True

    def _sincedb_start_position(self, file, fid=None):
        """Retrieves the starting position from the sincedb sql db
        for a given file
        """
        if not self._sincedb_path:
            return None

        if not fid:
            fid = self.get_file_id(os.stat(file.name))

        self._sincedb_init()
        conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute("select position from sincedb where fid = :fid and filename = :filename", {
            'fid': fid,
            'filename': file.name
        })

        start_position = None
        for row in cursor.fetchall():
            start_position, = row

        return start_position

    def update_files(self):
        """Ensures all files are properly loaded.
        Detects new files, file removals, file rotation, and truncation.
        On non-linux platforms, it will also manually reload the file for tailing.
        Note that this hack is necessary because EOF is cached on BSD systems.
        """
        self._update_time = int(time.time())

        ls = []
        files = []
        if len(self._beaver_config.get('globs')) > 0:
            for name, exclude in self._beaver_config.get('globs').items():
                globbed = [os.path.realpath(filename) for filename in eglob(name, exclude)]
                files.extend(globbed)
                self._file_config.addglob(name, globbed)
                self._callback(("addglob", (name, globbed)))
        else:
            for name in self.listdir():
                files.append(os.path.realpath(os.path.join(self._folder, name)))

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
        for fid, data in self._file_map.iteritems():
            try:
                st = os.stat(data['file'].name)
            except EnvironmentError, err:
                if err.errno == errno.ENOENT:
                    self.unwatch(data['file'], fid)
                else:
                    raise
            else:
                if fid != self.get_file_id(st):
                    self._logger.info("[{0}] - file rotated {1}".format(fid, data['file'].name))
                    self.unwatch(data['file'], fid)
                    self.watch(data['file'].name)
                elif data['file'].tell() > st.st_size:
                    if st.st_size == 0 and self._file_config.get('ignore_truncate', data['file'].name):
                        self._logger.info("[{0}] - file size is 0 {1}. ".format(fid, data['file'].name) +
                                          "If you use another tool (i.e. logrotate) to truncate " +
                                          "the file, your application may continue to write to " +
                                          "the offset it last wrote later. In such a case, we'd " +
                                          "better do nothing here")
                        continue
                    self._logger.info("[{0}] - file truncated {1}".format(fid, data['file'].name))
                    self.unwatch(data['file'], fid)
                    self.watch(data['file'].name)
                elif REOPEN_FILES:
                    self._logger.debug("[{0}] - file reloaded (non-linux) {1}".format(fid, data['file'].name))
                    position = data['file'].tell()
                    fname = data['file'].name
                    data['file'].close()
                    file = self.open(fname, encoding=data['encoding'])
                    file.seek(position)
                    self._file_map[fid]['file'] = file

        # add new ones
        for fid, fname in ls:
            if fid not in self._file_map:
                self.watch(fname)

    def unwatch(self, file, fid):
        """file no longer exists; if it has been renamed
        try to read it for the last time in case the
        log rotator has written something in it.
        """
        try:
            self.readfile(fid, file)
        except IOError:
            # Silently ignore any IOErrors -- file is gone
            pass
        self._logger.info("[{0}] - un-watching logfile {1}".format(fid, file.name))
        del self._file_map[fid]

    def watch(self, fname):
        """Opens a file for log tailing"""
        try:
            file = self.open(fname, encoding=self._file_config.get('encoding', fname))
            fid = self.get_file_id(os.stat(fname))
        except EnvironmentError, err:
            if err.errno != errno.ENOENT:
                raise
        else:
            self._logger.info("[{0}] - watching logfile {1}".format(fid, fname))
            self._file_map[fid] = {
                'encoding': self._file_config.get('encoding', fname),
                'file': file,
                'line': 0,
                'update_time': None,
            }

    @classmethod
    def open(cls, fname, encoding=None):
        """Opens a file with the appropriate call"""
        if IS_GZIPPED_FILE.search(fname):
            file = gzip.open(fname, "rb")
        else:
            if encoding:
                file = io.open(fname, "r", encoding=encoding)
            else:
                file = io.open(fname, "r")

        return file

    @staticmethod
    def get_file_id(st):
        return "%xg%x" % (st.st_dev, st.st_ino)

    @classmethod
    def tail(cls, fname, encoding, window, position=None):
        """Read last N lines from file fname."""
        if window <= 0:
            raise ValueError('invalid window %r' % window)

        encodings = ENCODINGS
        if encoding:
            encodings = [encoding] + ENCODINGS

        for enc in encodings:
            try:
                f = cls.open(fname, encoding=enc)
                return cls.tail_read(f, window, position=position)
            except IOError, err:
                if err.errno == errno.ENOENT:
                    return []
                raise
            except UnicodeDecodeError:
                pass

    @classmethod
    def tail_read(cls, f, window, position=None):
        BUFSIZ = 1024
        # open() was overridden and file was opened in text
        # mode; read() will return a string instead bytes.
        encoded = getattr(f, 'encoding', False)
        CR = '\n' if encoded else b'\n'
        data = '' if encoded else b''
        f.seek(0, os.SEEK_END)
        if position is None:
            position = f.tell()

        block = -1
        exit = False
        read = BUFSIZ

        while not exit:
            step = (block * BUFSIZ) + position
            if step < 0:
                step = 0
                read = ((block + 1) * BUFSIZ) + position
                exit = True

            f.seek(step, os.SEEK_SET)
            newdata = f.read(read)

            data = newdata + data
            if data.count(CR) > window:
                break
            else:
                block -= 1

        return data.splitlines()[-window:]
