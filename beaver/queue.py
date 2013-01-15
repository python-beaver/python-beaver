import signal
import sys
import time

from transport import TransportException, create_transport


def run_queue(queue, beaver_config, file_config, logger=None):
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    signal.signal(signal.SIGQUIT, signal.SIG_DFL)

    transport = None
    try:
        logger.debug("Logging using the {0} transport".format(beaver_config.get('transport')))
        transport = create_transport(beaver_config, file_config, logger=logger)

        failure_count = 0
        while True:
            command, data = queue.get()
            if command == "callback":
                try:
                    transport.callback(*data)
                except TransportException:
                    failure_count = failure_count + 1
                    if failure_count > int(beaver_config.get('max_failure')):
                        failure_count = int(beaver_config.get('max_failure'))

                    sleep_time = int(beaver_config.get('respawn_delay')) ** failure_count
                    logger.info("Caught transport exception, respawning in %d seconds" % sleep_time)

                    try:
                        time.sleep(sleep_time)
                    except KeyboardInterrupt:
                        logger.info("User cancelled respawn.")
                        transport.interrupt()

                        sys.exit(0)
            elif command == "exit":
                break
    except KeyboardInterrupt:
        logger.debug("Queue Interruped")
        if transport is not None:
            transport.interrupt()

        logger.debug("Queue Shutdown")
