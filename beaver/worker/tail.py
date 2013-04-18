# -*- coding: utf-8 -*-
# file tailer
import datetime
import errno
import gzip
import io
import os
import sqlite3
import time

from beaver.utils import IS_GZIPPED_FILE, REOPEN_FILES
from beaver.unicode_dammit import ENCODINGS
from beaver.worker.base_log import BaseLog


class Tail(BaseLog):
    """Follows a single file and outputs new lines from it to a callback
    """

    def __init__(self, filename, callback, position="end", logger=None, beaver_config=None, file_config=None):
        super(Tail, self).__init__(logger=logger)

        self.active = False
        self._callback = callback
        self._fid = None
        self._file = None
        self._filename = filename
        self._last_sincedb_write = None
        self._last_file_mapping_update = None
        self._line_count = 0
        self._log_template = '[' + self._filename + '] - {0}'

        self._sincedb_path = beaver_config.get('sincedb_path')

        self._debug = file_config.get('debug', filename)  # TODO: Implement me
        self._encoding = file_config.get('encoding', filename)
        self._fields = file_config.get('fields', filename)
        self._format = file_config.get('format', filename)
        self._ignore_empty = file_config.get('ignore_empty', filename)
        self._ignore_truncate = file_config.get('ignore_truncate', filename)
        self._message_format = file_config.get('message_format', filename)  # TODO: Implement me
        self._sincedb_write_interval = file_config.get('sincedb_write_interval', filename)
        self._start_position = file_config.get('start_position', filename)
        self._stat_interval = file_config.get('stat_interval', filename)
        self._tail_lines = file_config.get('tail_lines', filename)
        self._tags = file_config.get('tags', filename)
        self._type = file_config.get('type', filename)

        self._update_file()
        self._log_info("watching logfile")

    def __del__(self):
        """Closes all files"""
        self.close()

    def open(self, encoding=None):
        """Opens the file with the appropriate call"""
        if IS_GZIPPED_FILE.search(self._filename):
            _file = gzip.open(self._filename, 'rb')
        else:
            if encoding:
                _file = io.open(self._filename, 'r', encoding=encoding)
            elif self._encoding:
                _file = io.open(self._filename, 'r', encoding=self._encoding)
            else:
                _file = io.open(self._filename, 'r')

        return _file

    def close(self):
        """Closes all currently open file pointers"""
        self.active = False
        if self._file:
            self._file.close()

    def run(self, once=False):
        while self.active:
            current_time = time.time()
            self._run_pass()

            self._ensure_file_is_good(current_time=current_time)

            self._log_debug('Iteration took {0:.6f}'.format(time.time() - current_time))
            if once:
                break

        if not once:
            self._log_debug('file closed')

    def fid(self):
        return self._fid

    def _ensure_file_is_good(self, current_time):
        """Every N seconds, ensures that the file we are tailing is the file we expect to be tailing"""
        if self._last_file_mapping_update and current_time - self._last_file_mapping_update <= self._stat_interval:
            return

        self._last_file_mapping_update = time.time()

        try:
            st = os.stat(self._filename)
        except EnvironmentError, err:
            if err.errno == errno.ENOENT:
                self._log_info('file removed')
                self.close()

        fid = self.get_file_id(st)
        if fid != self._fid:
            self._log_info('file rotated')
            self.close()
        elif self._file.tell() > st.st_size:
            if st.st_size == 0 and self._ignore_truncate:
                self._logger.info("[{0}] - file size is 0 {1}. ".format(fid, self._filename) +
                                  "If you use another tool (i.e. logrotate) to truncate " +
                                  "the file, your application may continue to write to " +
                                  "the offset it last wrote later. In such a case, we'd " +
                                  "better do nothing here")
                return
            self._log_info('file truncated')
            self._update_file(seek_to_end=False)
        elif REOPEN_FILES:
            self._log_debug('file reloaded (non-linux)')
            position = self._file.tell()
            self._update_file(seek_to_end=False)
            self._file.seek(position, os.SEEK_SET)

    def _run_pass(self):
        """Read lines from a file and performs a callback against them"""
        line_count = 0
        while True:
            try:
                lines = self._file.readlines(4096)
            except IOError, e:
                if e.errno == errno.ESTALE:
                    self.active = False
                    return False

            if not lines:
                break

            self._callback_wrapper(lines)

            if self._sincedb_path:
                current_line_count = len(lines)
                if not self._sincedb_update_position(lines=current_line_count):
                    line_count += current_line_count

        if line_count > 0:
            self._sincedb_update_position(lines=line_count, force_update=True)

    def _callback_wrapper(self, lines):
        self._callback(('callback', {
            'fields': self._fields,
            'filename': self._filename,
            'format': self._format,
            'ignore_empty': self._ignore_empty,
            'lines': lines,
            'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
            'tags': self._tags,
            'type': self._type,
        }))

    def _seek_to_end(self):
        self._log_debug('seek_to_end')

        if self._sincedb_path:
            sincedb_start_position = self._sincedb_start_position()
            if sincedb_start_position:
                self._start_position = sincedb_start_position

        if self._start_position == 'beginning':
            self._log_debug('no start_position specified')
            return

        line_count = 0

        if str(self._start_position).isdigit():
            self._log_debug('going to start position {0}'.format(self._start_position))
            self._start_position = int(self._start_position)
            for encoding in ENCODINGS:
                line_count, encoded = self._seek_to_position(encoding=encoding, position=True)
                if encoded:
                    break

        if self._start_position == 'beginning':
            self._log_debug('Bad start position specified')
            return

        if self._start_position == 'end':
            self._log_debug('getting end position')
            for encoding in ENCODINGS:
                line_count, encoded = self._seek_to_position(encoding=encoding)
                if encoded:
                    break

        current_position = self._file.tell()
        self._log_debug('line count {0}'.format(line_count))
        self._log_debug('current position {0}'.format(current_position))
        self._sincedb_update_position(lines=line_count, force_update=True)

        if self._tail_lines:
            self._log_debug('tailing {0} lines'.format(self._tail_lines))
            lines = self.tail(self._filename, encoding=self._encoding, window=self._tail_lines, position=current_position)
            if lines:
                self._callback_wrapper(lines)

    def _seek_to_position(self, encoding=None, position=None):
        line_count = 0
        encoded = False
        try:
            while self._file.readline():
                line_count += 1
                if position and line_count == self._start_position:
                    encoded = True
                    break

            if not position:
                encoded = True
        except UnicodeDecodeError:
            self._log_debug('UnicodeDecodeError raised with encoding {0}'.format(self._encoding))
            self._file = self.open(encoding=encoding)
            self._encoding = encoding

        if position and line_count != self._start_position:
            self._log_debug('file at different position than {0}, assuming manual truncate'.format(self._start_position))
            self._file.seek(0, os.SEEK_SET)
            self._start_position == 'beginning'

        return line_count, encoded

    def _sincedb_init(self):
        """Initializes the sincedb schema in an sqlite db"""
        if not self._sincedb_path:
            return

        if not os.path.exists(self._sincedb_path):
            self._log_debug('initializing sincedb sqlite schema')
            conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
            conn.execute("""
            create table sincedb (
                fid      text primary key,
                filename text,
                position integer default 1
            );
            """)
            conn.close()

    def _sincedb_update_position(self, lines=0, force_update=False):
        """Retrieves the starting position from the sincedb sql db for a given file
        Returns a boolean representing whether or not it updated the record
        """
        if not self._sincedb_path:
            return False

        current_time = int(time.time())
        if not force_update:
            if self._last_sincedb_write and current_time - self._last_sincedb_write <= self._sincedb_write_interval:
                return False

            if lines == 0:
                return False

        self._sincedb_init()

        old_count = self._line_count
        self._last_sincedb_write = current_time
        self._line_count = old_count + lines
        lines = self._line_count

        self._log_debug('updating sincedb to {0}'.format(lines))

        conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
        cursor = conn.cursor()
        query = 'insert or ignore into sincedb (fid, filename) values (:fid, :filename);'
        cursor.execute(query, {
            'fid': self._fid,
            'filename': self._filename
        })

        query = 'update sincedb set position = :position where fid = :fid and filename = :filename'
        cursor.execute(query, {
            'fid': self._fid,
            'filename': self._filename,
            'position': lines,
        })
        conn.close()

        return True

    def _sincedb_start_position(self):
        """Retrieves the starting position from the sincedb sql db
        for a given file
        """
        if not self._sincedb_path:
            return None

        self._sincedb_init()
        self._log_debug('retrieving start_position from sincedb')
        conn = sqlite3.connect(self._sincedb_path, isolation_level=None)
        cursor = conn.cursor()
        cursor.execute('select position from sincedb where fid = :fid and filename = :filename', {
            'fid': self._fid,
            'filename': self._filename
        })

        start_position = None
        for row in cursor.fetchall():
            start_position, = row

        return start_position

    def _update_file(self, seek_to_end=True):
        """Open the file for tailing"""
        try:
            self.close()
            self._file = self.open()
        except IOError:
            pass
        else:
            self.active = True
            try:
                st = os.stat(self._filename)
            except EnvironmentError, err:
                if err.errno == errno.ENOENT:
                    self._log_info('file removed')
                    self.close()

            fid = self.get_file_id(st)
            if not self._fid:
                self._fid = fid

            if fid != self._fid:
                self._log_info('file rotated')
                self.close()
            elif seek_to_end:
                self._seek_to_end()

    def tail(self, fname, encoding, window, position=None):
        """Read last N lines from file fname."""
        if window <= 0:
            raise ValueError('invalid window %r' % window)

        encodings = ENCODINGS
        if encoding:
            encodings = [encoding] + ENCODINGS

        for enc in encodings:
            try:
                f = self.open(encoding=enc)
                return self.tail_read(f, window, position=position)
            except IOError, err:
                if err.errno == errno.ENOENT:
                    return []
                raise
            except UnicodeDecodeError:
                pass

    @staticmethod
    def get_file_id(st):
        return "%xg%x" % (st.st_dev, st.st_ino)

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
