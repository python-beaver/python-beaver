import sys
import time

from beaver.config import FileConfig, BeaverConfig
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.transport import TransportException, create_transport
from beaver.utils import setup_custom_logger, version
from beaver.worker import Worker, REOPEN_FILES

__version__ = '15'


def run(args):
    version(args)

    logger = setup_custom_logger('beaver', args)

    file_config = FileConfig(args, logger=logger)
    beaver_config = BeaverConfig(args, file_config=file_config, logger=logger)
    ssh_tunnel = create_ssh_tunnel(beaver_config)

    failure_count = 0
    while 1:
        try:
            logger.debug("Logging using the {0} transport".format(beaver_config.get('transport')))
            transport = create_transport(beaver_config, file_config)

            if REOPEN_FILES:
                logger.debug("Detected non-linux platform. Files will be reopened for tailing")

            logger.info("Starting worker...")
            worker = Worker(beaver_config, file_config, transport.callback, logger=logger)

            logger.info("Working...")
            worker.loop()

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
                if ssh_tunnel is not None:
                    logger.info("Closing ssh tunnel.")
                    ssh_tunnel.close()

                sys.exit(0)

        except KeyboardInterrupt:
            logger.info("Shutting down. Please wait.")
            transport.interrupt()
            worker.close()
            if ssh_tunnel is not None:
                logger.info("Closing ssh tunnel.")
                ssh_tunnel.close()

            logger.info("Shutdown complete.")
            sys.exit(0)
