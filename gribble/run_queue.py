# -*- coding: utf-8 -*-
import Queue
import signal
import sys
import time

from beaver.transports import create_transport
from beaver.transports.exception import TransportException
from unicode_dammit import unicode_dammit


def run_queue(queue, beaver_config, logger=None):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGQUIT, signal.SIG_DFL)

    last_update_time = int(time.time())
    queue_timeout = beaver_config.get('queue_timeout')
    wait_timeout = beaver_config.get('wait_timeout')
    count = 0

    transport = None
    try:
        logger.debug('Logging using the {0} transport'.format(beaver_config.get('transport')))
        transport = create_transport(beaver_config, logger=logger)

        failure_count = 0
        while True:
            if not transport.valid():
                logger.info('Transport connection issues, stopping queue')
                break

            if int(time.time()) - last_update_time > queue_timeout:
                logger.info('Queue timeout of "{0}" seconds exceeded, stopping queue'.format(queue_timeout))
                break

            command = None
            try:
                if queue.full():
                    logger.error("Queue is full")

                else:
                    if count == 1000:
                        logger.debug("Main consumer queue Size is: " + str(queue.qsize()))
                        count = 0
                command, data = queue.get(block=True, timeout=wait_timeout)
                if command == "callback":
                    last_update_time = int(time.time())
                    logger.debug('Last update time now {0}'.format(last_update_time))
            except Queue.Empty:
                if not queue.empty():
                    logger.error('Recieved timeout from main consumer queue - stopping queue')
                    break
                else:
                    logger.debug('No data')

            if command == 'callback':
                if data.get('ignore_empty', False):
                    logger.debug('removing empty lines')
                    lines = data['lines']
                    new_lines = []
                    for line in lines:
                        message = unicode_dammit(line)
                        if len(message) == 0:
                            continue
                        new_lines.append(message)
                    data['lines'] = new_lines

                if len(data['lines']) == 0:
                    logger.debug('0 active lines sent from worker')
                    continue

                while True:
                    try:
                        transport.callback(**data)
                        count += 1
                        logger.debug("Number of transports: " + str(count))
                        break
                    except TransportException:
                        failure_count = failure_count + 1
                        if failure_count > beaver_config.get('max_failure'):
                            failure_count = beaver_config.get('max_failure')

                        sleep_time = beaver_config.get('respawn_delay') ** failure_count
                        logger.info('Caught transport exception, reconnecting in %d seconds' % sleep_time)

                        try:
                            transport.invalidate()
                            time.sleep(sleep_time)
                            transport.reconnect()
                            if transport.valid():
                                failure_count = 0
                                logger.info('Reconnected successfully')
                        except KeyboardInterrupt:
                            logger.info('User cancelled respawn.')
                            transport.interrupt()
                            sys.exit(0)
            elif command == 'addglob':
                beaver_config.addglob(*data)
                transport.addglob(*data)
            elif command == 'exit':
                break
    except KeyboardInterrupt:
        logger.debug('Queue Interruped')
        if transport is not None:
            transport.interrupt()

        logger.debug('Queue Shutdown')
