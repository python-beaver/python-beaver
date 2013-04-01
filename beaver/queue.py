import os
import Queue
import signal
import sys
import time

from transport import TransportException, create_transport


def run_queue(queue, beaver_config, file_config, logger=None):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGQUIT, signal.SIG_DFL)

    last_update_time = int(time.time())
    queue_timeout = beaver_config.get('queue_timeout')
    wait_timeout = beaver_config.get('wait_timeout')

    transport = None
    try:
        logger.debug("Logging using the {0} transport".format(beaver_config.get('transport')))
        transport = create_transport(beaver_config, file_config, logger=logger)

        failure_count = 0
        while True:
            if not transport.valid():
                logger.info("Transport connection issues, stopping queue")
                break

            if int(time.time()) - last_update_time > queue_timeout:
                logger.info("Queue timeout of '{0}' seconds exceeded, stopping queue".format(queue_timeout))
                break

            try:
                command, data = queue.get(block=True, timeout=wait_timeout)
                last_update_time = int(time.time())
                logger.debug("Last update time now {0}".format(last_update_time))
            except Queue.Empty:
                logger.debug("No data")
                continue

            if command == "callback":
                try:
                    if file_config.get('ignore_empty', data['filename']):
                        logger.debug("removing empty lines")
                        lines = data['lines']
                        new_lines = []
                        for line in lines:
                            message = line.strip(os.linesep)
                            if len(message) == 0:
                                continue
                            new_lines.append(message)
                        data['lines'] = new_lines

                    if len(data['lines']) == 0:
                        logger.debug("0 active lines sent from worker")
                        continue

                    transport.callback(**data)
                except TransportException:
                    failure_count = failure_count + 1
                    if failure_count > beaver_config.get('max_failure'):
                        failure_count = beaver_config.get('max_failure')

                    sleep_time = int(beaver_config.get('respawn_delay')) ** failure_count
                    logger.info("Caught transport exception, respawning in %d seconds" % sleep_time)

                    try:
                        time.sleep(sleep_time)
                        transport.reconnect()
                    except KeyboardInterrupt:
                        logger.info("User cancelled respawn.")
                        transport.interrupt()

                        sys.exit(0)
            elif command == "addglob":
                file_config.addglob(*data)
                transport.addglob(*data)
            elif command == "exit":
                break
    except KeyboardInterrupt:
        logger.debug("Queue Interruped")
        if transport is not None:
            transport.interrupt()

        logger.debug("Queue Shutdown")
