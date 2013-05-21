# -*- coding: utf-8 -*-
import collections
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

    def __init__(self, beaver_config, queue_consumer_function, callback, logger=None):
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
        self._file_map = {}
        self._folder = self._beaver_config.get('path')
        self._last_file_mapping_update = {}
        self._logger = logger
        self._proc = None
        self._sincedb_path = self._beaver_config.get('sincedb_path')
        self._update_time = None

        if not callable(self._callback):
            raise RuntimeError("Callback for worker is not callable")

        self.update_files()
        self._seek_to_end()

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

            self._ensure_files_are_good(current_time=t)

            unwatch_list = []

            for fid, data in self._file_map.iteritems():
                try:
                    self._run_pass(fid, data['file'])
                except IOError, e:
                    if e.errno == errno.ESTALE:
                        unwatch_list.append(fid)

            self.unwatch_list(unwatch_list)

            if async:
                return

            self._logger.debug("Iteration took {0:.6f}".format(time.time() - t))
            time.sleep(interval)

    def _run_pass(self, fid, file):
        """Read lines from a file and performs a callback against them"""
        line_count = 0
        while True:
            try:
                data = file.read(4096)
            except IOError, e:
                if e.errno == errno.ESTALE:
                    self.active = False
                    return False

            lines = self._buffer_extract(data=data, fid=fid)

            if not lines:
                break

            self._callback_wrapper(filename=file.name, lines=lines)

            if self._sincedb_path:
                current_line_count = len(lines)
                if not self._sincedb_update_position(file, fid=fid, lines=current_line_count):
                    line_count += current_line_count

        if line_count > 0:
            self._sincedb_update_position(file, fid=fid, lines=line_count, force_update=True)

    def _buffer_extract(self, data, fid):
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
        entities = collections.deque(data.split(self._file_map[fid]['delimiter'], -1))

        # Check to see if the buffer has exceeded capacity, if we're imposing a limit
        if self._file_map[fid]['size_limit']:
            if self._file_map[fid]['input_size'] + len(entities[0]) > self._file_map[fid]['size_limit']:
                raise Exception('input buffer full')
            self._file_map[fid]['input_size'] += len(entities[0])

        # Move the first entry in the resulting array into the input buffer.  It represents
        # the last segment of a token-delimited entity unless it's the only entry in the list.
        self._file_map[fid]['input'].append(entities.popleft())

        # If the resulting array from the split is empty, the token was not encountered
        # (not even at the end of the buffer).  Since we've encountered no token-delimited
        # entities this go-around, return an empty array.
        if len(entities) == 0:
            return []

        # At this point, we've hit a token, or potentially multiple tokens.  Now we can bring
        # together all the data we've buffered from earlier calls without hitting a token,
        # and add it to our list of discovered entities.
        entities.appendleft(''.join(self._file_map[fid]['input']))

        # Now that we've hit a token, joined the input buffer and added it to the entities
        # list, we can go ahead and clear the input buffer.  All of the segments that were
        # stored before the join can now be garbage collected.
        self._file_map[fid]['input'].clear()

        # The last entity in the list is not token delimited, however, thanks to the -1
        # passed to split.  It represents the beginning of a new list of as-yet-untokenized
        # data, so we add it to the start of the list.
        self._file_map[fid]['input'].append(entities.pop())

        # Set the new input buffer size, provided we're keeping track
        if self._file_map[fid]['size_limit']:
            self._file_map[fid]['input_size'] = len(self._file_map[fid]['input'][0])

        # Now we're left with the list of extracted token-delimited entities we wanted
        # in the first place.  Hooray!
        return entities

    # Flush the contents of the input buffer, i.e. return the input buffer even though
    # a token has not yet been encountered
    def _buffer_flush(self, fid):
        buf = ''.join(self._file_map[fid]['input'])
        self._file_map[fid]['input'].clear
        return buf

    # Is the buffer empty?
    def _buffer_empty(self, fid):
        return len(self._file_map[fid]['input']) > 0

    def _seek_to_end(self):
        unwatch_list = []

        # The first time we run the script we move all file markers at EOF.
        # In case of files created afterwards we don't do this.
        for fid, data in self._file_map.iteritems():
            self._logger.debug("[{0}] - getting start position {1}".format(fid, data['file'].name))
            start_position = self._beaver_config.get_field('start_position', data['file'].name)
            is_active = data['active']

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
                        if not data['file']:
                            unwatch_list.append(fid)
                            is_active = False
                            break

                        data['encoding'] = encoding

                    if line_count != start_position:
                        self._logger.debug("[{0}] - file at different position than {1}, assuming manual truncate for {2}".format(fid, start_position, data['file'].name))
                        data['file'].seek(0, os.SEEK_SET)
                        start_position == "beginning"

            if not is_active:
                continue

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
                        if not data['file']:
                            unwatch_list.append(fid)
                            is_active = False
                            break

                        data['encoding'] = encoding

            if not is_active:
                continue

            current_position = data['file'].tell()
            self._logger.debug("[{0}] - line count {1} for {2}".format(fid, line_count, data['file'].name))
            self._sincedb_update_position(data['file'], fid=fid, lines=line_count, force_update=True)

            tail_lines = self._beaver_config.get_field('tail_lines', data['file'].name)
            tail_lines = int(tail_lines)
            if tail_lines:
                encoding = data['encoding']

                lines = self.tail(data['file'].name, encoding=encoding, window=tail_lines, position=current_position)
                if lines:
                    self._callback_wrapper(filename=data['file'].name, lines=lines)

        self.unwatch_list(unwatch_list)

    def _callback_wrapper(self, filename, lines):
        self._callback(('callback', {
            'fields': self._beaver_config.get_field('fields', filename),
            'filename': filename,
            'format': self._beaver_config.get_field('format', filename),
            'ignore_empty': self._beaver_config.get_field('ignore_empty', filename),
            'lines': lines,
            'timestamp': datetime.datetime.utcnow().isoformat() + "Z",
            'tags': self._beaver_config.get_field('tags', filename),
            'type': self._beaver_config.get_field('type', filename),
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
            sincedb_write_interval = self._beaver_config.get_field('sincedb_write_interval', file.name)
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
                self._beaver_config.addglob(name, globbed)
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

        # add new ones
        for fid, fname in ls:
            if fid not in self._file_map:
                self.watch(fname)

    def _ensure_files_are_good(self, current_time):
        """Every N seconds, ensures that the file we are tailing is the file we expect to be tailing"""

        # We cannot watch/unwatch in a single iteration
        rewatch_list = []
        unwatch_list = []

        # check existent files
        for fid, data in self._file_map.iteritems():
            filename = data['file'].name
            stat_interval = self._beaver_config.get_field('stat_interval', filename)
            if filename in self._last_file_mapping_update and current_time - self._last_file_mapping_update[filename] <= stat_interval:
                continue

            self._last_file_mapping_update[filename] = time.time()

            try:
                st = os.stat(data['file'].name)
            except EnvironmentError, err:
                if err.errno == errno.ENOENT:
                    unwatch_list.append(fid)
                else:
                    raise
            else:
                if fid != self.get_file_id(st):
                    self._logger.info("[{0}] - file rotated {1}".format(fid, data['file'].name))
                    rewatch_list.append(fid)
                elif data['file'].tell() > st.st_size:
                    if st.st_size == 0 and self._beaver_config.get_field('ignore_truncate', data['file'].name):
                        self._logger.info("[{0}] - file size is 0 {1}. ".format(fid, data['file'].name) +
                                          "If you use another tool (i.e. logrotate) to truncate " +
                                          "the file, your application may continue to write to " +
                                          "the offset it last wrote later. In such a case, we'd " +
                                          "better do nothing here")
                        continue
                    self._logger.info("[{0}] - file truncated {1}".format(fid, data['file'].name))
                    rewatch_list.append(fid)
                elif REOPEN_FILES:
                    self._logger.debug("[{0}] - file reloaded (non-linux) {1}".format(fid, data['file'].name))
                    position = data['file'].tell()
                    fname = data['file'].name
                    data['file'].close()
                    file = self.open(fname, encoding=data['encoding'])
                    if file:
                        file.seek(position)
                        self._file_map[fid]['file'] = file

        self.unwatch_list(unwatch_list)
        self.rewatch_list(rewatch_list)

    def rewatch_list(self, rewatch_list):
        for fid in rewatch_list:
            if fid not in self._file_map:
                continue

            f = self._file_map[fid]['file']
            filename = f.name
            self.unwatch(f, fid)
            self.watch(filename)

    def unwatch_list(self, unwatch_list):
        for fid in unwatch_list:
            if fid not in self._file_map:
                continue

            f = self._file_map[fid]['file']
            self.unwatch(f, fid)

    def unwatch(self, file, fid):
        """file no longer exists; if it has been renamed
        try to read it for the last time in case the
        log rotator has written something in it.
        """
        try:
            if file:
                self._run_pass(fid, file)
        except IOError:
            # Silently ignore any IOErrors -- file is gone
            pass

        if file:
            self._logger.info("[{0}] - un-watching logfile {1}".format(fid, file.name))
        else:
            self._logger.info("[{0}] - un-watching logfile".format(fid))

        del self._file_map[fid]

    def watch(self, fname):
        """Opens a file for log tailing"""
        try:
            file = self.open(fname, encoding=self._beaver_config.get_field('encoding', fname))
            if file:
                fid = self.get_file_id(os.stat(fname))
        except EnvironmentError, err:
            if err.errno != errno.ENOENT:
                raise
        else:
            if file:
                self._logger.info("[{0}] - watching logfile {1}".format(fid, fname))
                self._file_map[fid] = {
                    'delimiter': self._beaver_config.get_field('delimiter', fname),
                    'encoding': self._beaver_config.get_field('encoding', fname),
                    'file': file,
                    'input': collections.deque([]),
                    'input_size': 0,
                    'line': 0,
                    'size_limit': self._beaver_config.get_field('size_limit', fname),
                    'update_time': None,
                    'active': True,
                }

    def open(self, filename, encoding=None):
        """Opens a file with the appropriate call"""
        try:
            if IS_GZIPPED_FILE.search(filename):
                _file = gzip.open(filename, "rb")
            else:
                file_encoding = self._beaver_config.get_field('encoding', filename)
                if encoding:
                    _file = io.open(filename, "r", encoding=encoding)
                elif file_encoding:
                    _file = io.open(filename, "r", encoding=file_encoding)
                else:
                    _file = io.open(filename, "r")
        except IOError, e:
            self._logger.warning(str(e))
            _file = None

        return _file

    def tail(self, fname, encoding, window, position=None):
        """Read last N lines from file fname."""
        if window <= 0:
            raise ValueError('invalid window %r' % window)

        encodings = ENCODINGS
        if encoding:
            encodings = [encoding] + ENCODINGS

        for enc in encodings:
            try:
                f = self.open(fname, encoding=enc)
                if not f:
                    return []
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
