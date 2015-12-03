# -*- coding: utf-8 -*-
import Queue
import signal
import sys
import time

from beaver.transports import create_transport
from beaver.transports.exception import TransportException
from beaver.unicode_dammit import unicode_dammit


class RunQueue(object):
    """
    RunQueue responsible for processing logs, and calling
    transport callback to handle shipping
    """

    def __init__(self, queue, beaver_conf, logger=None):
        self.logger = logger
        self.beaver_conf = beaver_conf
        self.queue = queue

        self.last_update_time = int(time.time())
        self.queue_timeout = self.beaver_conf.get('queue_timeout')
        self.wait_timeout = self.beaver_conf.get('wait_timeout')

        self.transport = None

    def get_connection_status(self):
        """Returns true if self.transport is valid"""
        if self.transport is None:
            return False
        return self.transport.is_valid()

    def get_queue_size(self):
        """Returns the current number of logs still to be processed"""
        #TODO: make queue copy and itterate counting number of 
        # of callback commands
        return self.queue.qsize()

    def loop(self):
        """Main loop, processes and ships logs"""
        try:
            self.logger.debug('Logging using the {0} self.transport'.
                    format(self.beaver_conf.get('self.transport')))
            self.transport = create_transport(
                    self.beaver_conf, logger=self.logger)
            fail_count = 0
            while True:
                if not self.transport.valid():
                    self.logger.info('Transport connection issues',
                            'stopping queue')
                    break
                c_time = int(time.time())
                if c_time - self.last_update_time > self.queue_timeout:
                    self.logger.info('Queue timeout of "{0} seconds exceeded'\
                            'stopping self.queue'.format(self.queue_timeout))
                    break

                try:
                    command, data = self.queue.get(block=True,
                            timeout=self.wait_timeout)
                    if command == "callback":
                        last_update_time = int(time.time())
                        self.logger.debug('Last update time now {0}'.
                                format(last_update_time))
                except Queue.Empty:
                    self.logger.debug('No Data')
                    continue

                if command == "callback":
                    if data.get('ignore_empty', False):
                        self.logger.debug('removing empty lines')
                        lines = data['lines']
                        new_lines = []
                        for line in lines:
                            message = unicode_dammit(line)
                            if len(message) == 0:
                                continue
                            new_lines.append(message)
                        data['lines'] = new_lines

                    if len(data['lines']) == 0:
                        self.logger.debuge('0 active lines sent from worked')
                        continue

                    while True:
                        try:
                            self.transport.callback(**data)
                            break
                        except TransportException:
                            fail_count = fail_count + 1
                            if fail_count > self.beaver_conf.get('max_failure'):
                                fail_count = self.beaver_conf.get('max_failure')

                            sleep_time = self.beaver_conf \
                                .get('respawn_delay') ** fail_count
                            self.logger.info('Caught self.transport exception',
                                ', reconnecting in %d seconds' % sleep_time)
                        try:
                            self.transport.invalidate()
                            time.sleep(sleep_time)
                            self.transport.reconnect()
                            if self.transport.valid():
                                fail_count = 0
                                self.logger.info('Reconnected successfully')
                        except KeyboardInterrupt:
                            self.logger.info('User cancelled respawn.')
                            self.transport.interrupt()
                            sys.exit(0)
                elif command == 'addglob':
                    self.beaver_conf.addglob(*data)
                    self.transport.addglob(*data)
                elif command == 'exit':
                    break
        except KeyboardInterrupt:
            self.logger.debug('Queue Interruped')
            if self.transport is not None:
                self.transport.interrupt()

            self.logger.debug('Queue Shutdown')
        self.close()

    def close(self):
        """Close transport connection"""
        if self.transport is not None:
            self.transport.interrupt()
        self.logger.debug('Queue Shutdown')
