# -*- coding: utf-8 -*-
import collections
import datetime
import errno
import gzip
import io
import os
import sqlite3
import time

from beaver.utils import IS_GZIPPED_FILE, REOPEN_FILES, multiline_merge
from beaver.unicode_dammit import ENCODINGS
from beaver.base_log import BaseLog


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
        self._line_count_sincedb = 0
        self._log_template = '[' + self._filename + '] - {0}'

        self._sincedb_path = beaver_config.get('sincedb_path')

        self._debug = beaver_config.get_field('debug', filename)  # TODO: Implement me
        self._encoding = beaver_config.get_field('encoding', filename)
        self._fields = beaver_config.get_field('fields', filename)
        self._format = beaver_config.get_field('format', filename)
        self._ignore_empty = beaver_config.get_field('ignore_empty', filename)
        self._ignore_truncate = beaver_config.get_field('ignore_truncate', filename)
        self._message_format = beaver_config.get_field('message_format', filename)  # TODO: Implement me
        self._sincedb_write_interval = beaver_config.get_field('sincedb_write_interval', filename)
        self._start_position = beaver_config.get_field('start_position', filename)
        self._stat_interval = beaver_config.get_field('stat_interval', filename)
        self._tail_lines = beaver_config.get_field('tail_lines', filename)
        self._tags = beaver_config.get_field('tags', filename)
        self._type = beaver_config.get_field('type', filename)

        # The following is for the buffered tokenization
        # Store the specified delimiter
        self._delimiter = beaver_config.get_field("delimiter", filename)
        # Store the specified size limitation
        self._size_limit = beaver_config.get_field("size_limit", filename)
        # The input buffer is stored as an array.  This is by far the most efficient
        # approach given language constraints (in C a linked list would be a more
        # appropriate data structure).  Segments of input data are stored in a list
        # which is only joined when a token is reached, substantially reducing the
        # number of objects required for the operation.
        self._input = collections.deque([])

        # Size of the input buffer
        self._input_size = 0

        # Attribute for multi-line events
        self._current_event = collections.deque([])
        self._last_activity = time.time()
        self._multiline_regex_after = beaver_config.get_field('multiline_regex_after', filename)
        self._multiline_regex_before = beaver_config.get_field('multiline_regex_before', filename)

        self._update_file()
        if self.active:
            self._log_info("watching logfile")

    def __del__(self):
        """Closes all files"""
        self.close()

    def open(self, encoding=None):
        """Opens the file with the appropriate call"""
        try:
            if IS_GZIPPED_FILE.search(self._filename):
                _file = gzip.open(self._filename, 'rb')
            else:
                if encoding:
                    _file = io.open(self._filename, 'r', encoding=encoding, errors='replace')
                elif self._encoding:
                    _file = io.open(self._filename, 'r', encoding=self._encoding, errors='replace')
                else:
                    _file = io.open(self._filename, 'r', errors='replace')
        except IOError, e:
            self._log_warning(str(e))
            _file = None
            self.close()

        return _file

    def close(self):
        """Closes all currently open file pointers"""
        if not self.active:
            return

        self.active = False
        if self._file:
            self._file.close()
            self._sincedb_update_position(force_update=True)

        if self._current_event:
            event = '\n'.join(self._current_event)
            self._current_event.clear()
            self._callback_wrapper([event])

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

    def _buffer_extract(self, data):
        """
        Extract takes an arbitrary string of input data and returns an array of
        tokenized entities, provided there were any available to extract.  This
        makes for easy processing of datagrams using a pattern like:

          tokenizer.extract(data).map { |entity| Decode(entity) }.each do ..."""
        # Extract token-delimited entities from the input string with the split command.
        # There's a bit of craftiness here with the -1 parameter.  Normally split would
        # behave no differently regardless of if the token lies at the very end of the
        # input buffer or not (i.e. a literal edge case)  Specifying -1 forces split to
        # return "" in this case, meaning that the last entry in the list represents a
        # new segment of data where the token has not been encountered
        entities = collections.deque(data.split(self._delimiter, -1))

        # Check to see if the buffer has exceeded capacity, if we're imposing a limit
        if self._size_limit:
            if self.input_size + len(entities[0]) > self._size_limit:
                raise Exception('input buffer full')
            self._input_size += len(entities[0])

        # Move the first entry in the resulting array into the input buffer.  It represents
        # the last segment of a token-delimited entity unless it's the only entry in the list.
        first_entry = entities.popleft()
        if len(first_entry) > 0:
            self._input.append(first_entry)

        # If the resulting array from the split is empty, the token was not encountered
        # (not even at the end of the buffer).  Since we've encountered no token-delimited
        # entities this go-around, return an empty array.
        if len(entities) == 0:
            return []

        # At this point, we've hit a token, or potentially multiple tokens.  Now we can bring
        # together all the data we've buffered from earlier calls without hitting a token,
        # and add it to our list of discovered entities.
        entities.appendleft(''.join(self._input))

        # Now that we've hit a token, joined the input buffer and added it to the entities
        # list, we can go ahead and clear the input buffer.  All of the segments that were
        # stored before the join can now be garbage collected.
        self._input.clear()

        # The last entity in the list is not token delimited, however, thanks to the -1
        # passed to split.  It represents the beginning of a new list of as-yet-untokenized
        # data, so we add it to the start of the list.
        self._input.append(entities.pop())

        # Set the new input buffer size, provided we're keeping track
        if self._size_limit:
            self._input_size = len(self._input[0])

        # Now we're left with the list of extracted token-delimited entities we wanted
        # in the first place.  Hooray!
        return entities

    # Flush the contents of the input buffer, i.e. return the input buffer even though
    # a token has not yet been encountered
    def _buffer_flush(self):
        buf = ''.join(self._input)
        self._input.clear
        return buf

    # Is the buffer empty?
    def _buffer_empty(self):
        return len(self._input) > 0

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
            if self.active:
                self._file.seek(position, os.SEEK_SET)

    def _run_pass(self):
        """Read lines from a file and performs a callback against them"""
        while True:
            try:
                data = self._file.read(4096)
            except IOError, e:
                if e.errno == errno.ESTALE:
                    self.active = False
                    return False

            lines = self._buffer_extract(data)

            if not lines:
                # Before returning, check if an event (maybe partial) is waiting for too long.
                if self._current_event and time.time() - self._last_activity > 1:
                    event = '\n'.join(self._current_event)
                    self._current_event.clear()
                    self._callback_wrapper([event])
                break

            self._last_activity = time.time()

            if self._multiline_regex_after or self._multiline_regex_before:
                # Multiline is enabled for this file.
                events = multiline_merge(
                        lines,
                        self._current_event,
                        self._multiline_regex_after,
                        self._multiline_regex_before)
            else:
                events = lines

            if events:
                self._callback_wrapper(events)

            if self._sincedb_path:
                current_line_count = len(lines)
                self._sincedb_update_position(lines=current_line_count)

        self._sincedb_update_position()

    def _callback_wrapper(self, lines):
        now = datetime.datetime.utcnow()
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%S") + ".%03d" % (now.microsecond / 1000) + "Z"
        self._callback(('callback', {
            'fields': self._fields,
            'filename': self._filename,
            'format': self._format,
            'ignore_empty': self._ignore_empty,
            'lines': lines,
            'timestamp': timestamp,
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
                if line_count is None and encoded is None:
                    return

                if encoded:
                    break

        if self._start_position == 'beginning':
            self._log_debug('Bad start position specified')
            return

        if self._start_position == 'end':
            self._log_debug('getting end position')
            for encoding in ENCODINGS:
                line_count, encoded = self._seek_to_position(encoding=encoding)
                if line_count is None and encoded is None:
                    return

                if encoded:
                    break

        current_position = self._file.tell()
        self._log_debug('line count {0}'.format(line_count))
        self._log_debug('current position {0}'.format(current_position))
        self._sincedb_update_position(lines=line_count, force_update=True)
        # Reset this, so line added processed just after this initialization
        # will update the sincedb. Without this, if beaver run for less than
        # sincedb_write_interval it will always re-process the last lines.
        self._last_sincedb_write = 0

        if self._tail_lines:
            self._log_debug('tailing {0} lines'.format(self._tail_lines))
            lines = self.tail(self._filename, encoding=self._encoding, window=self._tail_lines, position=current_position)
            if lines:
                if self._multiline_regex_after or self._multiline_regex_before:
                    # Multiline is enabled for this file.
                    events = multiline_merge(
                            lines,
                            self._current_event,
                            self._multiline_regex_after,
                            self._multiline_regex_before)
                else:
                    events = lines
                self._callback_wrapper(events)

        return

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

        if not self._file:
            return None, None

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

        self._line_count = self._line_count + lines
        old_count = self._line_count_sincedb
        lines = self._line_count

        current_time = int(time.time())
        if not force_update:
            if self._last_sincedb_write and current_time - self._last_sincedb_write <= self._sincedb_write_interval:
                return False

            if old_count == lines:
                return False

        self._sincedb_init()

        self._last_sincedb_write = current_time

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

        self._line_count_sincedb = lines

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
            if not self._file:
                return

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
                if f:
                    return self.tail_read(f, window, position=position)

                return False
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
