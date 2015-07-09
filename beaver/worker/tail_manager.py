# -*- coding: utf-8 -*-
import errno
import os
import stat
import time
import signal
import threading

from beaver.utils import eglob
from beaver.base_log import BaseLog
from beaver.worker.tail import Tail


class TailManager(BaseLog):

    def __init__(self, beaver_config, queue_consumer_function, callback, logger=None):
        super(TailManager, self).__init__(logger=logger)
        self._active = False
        self._beaver_config = beaver_config
        self._folder = self._beaver_config.get('path')
        self._callback = callback
        self._create_queue_consumer = queue_consumer_function
        self._discover_interval = beaver_config.get('discover_interval', 15)
        self._log_template = "[TailManager] - {0}"
        self._number_of_consumer_processes = int(self._beaver_config.get('number_of_consumer_processes'))
        self._proc = [None] * self._number_of_consumer_processes
        self._tails = {}
        self._update_time = None

        self._active = True

        signal.signal(signal.SIGTERM, self.close)

    def listdir(self):
        """HACK around not having a beaver_config stanza
        TODO: Convert this to a glob"""
        ls = os.listdir(self._folder)
        return [x for x in ls if os.path.splitext(x)[1][1:] == "log"]

    def watch(self, paths=[]):
        for path in paths:
            if not self._active:
                break

            tail = Tail(
                filename=path,
                beaver_config=self._beaver_config,
                callback=self._callback,
                logger=self._logger
            )

            if tail.active:
                self._tails[tail.fid()] = tail

    def create_queue_consumer_if_required(self, interval=5.0):
        for n in range(0,self._number_of_consumer_processes):
            if not (self._proc[n] and self._proc[n].is_alive()):
                self._logger.debug("creating consumer process: " + str(n))
                self._proc[n] = self._create_queue_consumer()
        timer = threading.Timer(interval, self.create_queue_consumer_if_required)
        timer.start()

    def run(self, interval=0.1,):

        self.create_queue_consumer_if_required()

        while self._active:
            for fid in self._tails.keys():

                self.update_files()

                self._log_debug("Processing {0}".format(fid))
                if not self._active:
                    break

                self._tails[fid].run(once=True)

                if not self._tails[fid].active:
                    self._tails[fid].close()
                    del self._tails[fid]

            self.update_files()
            time.sleep(interval)

    def update_files(self):
        """Ensures all files are properly loaded.
        Detects new files, file removals, file rotation, and truncation.
        On non-linux platforms, it will also manually reload the file for tailing.
        Note that this hack is necessary because EOF is cached on BSD systems.
        """
        if self._update_time and int(time.time()) - self._update_time < self._discover_interval:
            return

        self._update_time = int(time.time())

        possible_files = []
        files = []
        if len(self._beaver_config.get('globs')) > 0:
            extend_files = files.extend
            for name, exclude in self._beaver_config.get('globs').items():
                globbed = [os.path.realpath(filename) for filename in eglob(name, exclude)]
                extend_files(globbed)
                self._beaver_config.addglob(name, globbed)
                self._callback(("addglob", (name, globbed)))
        else:
            append_files = files.append
            for name in self.listdir():
                append_files(os.path.realpath(os.path.join(self._folder, name)))

        for absname in files:
            try:
                st = os.stat(absname)
            except EnvironmentError, err:
                if err.errno != errno.ENOENT:
                    raise
            else:
                if not stat.S_ISREG(st.st_mode):
                    continue
                append_possible_files = possible_files.append
                fid = self.get_file_id(st)
                append_possible_files((fid, absname))

        # add new ones
        new_files = [fname for fid, fname in possible_files if fid not in self._tails]
        self.watch(new_files)

    def close(self, signalnum=None, frame=None):
        self._running = False
        """Closes all currently open Tail objects"""
        self._log_debug("Closing all tail objects")
        self._active = False
        for fid in self._tails:
            self._tails[fid].close()
        for n in range(0,self._number_of_consumer_processes):
            if self._proc[n] is not None and self._proc[n].is_alive():
                self._logger.debug("Terminate Process: " + str(n))
                self._proc[n].terminate()
                self._proc[n].join()

    @staticmethod
    def get_file_id(st):
        return "%xg%x" % (st.st_dev, st.st_ino)
