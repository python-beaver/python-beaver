import multiprocessing
import sys

from beaver.config import FileConfig, BeaverConfig
from beaver.queue import run_queue
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.utils import setup_custom_logger
from beaver.worker import Worker, REOPEN_FILES

__version__ = '20'


def run(args):
    logger = setup_custom_logger('beaver', args)

    file_config = FileConfig(args, logger=logger)
    beaver_config = BeaverConfig(args, file_config=file_config, logger=logger)
    ssh_tunnel = create_ssh_tunnel(beaver_config, logger=logger)

    queue = multiprocessing.Queue(beaver_config.get('max_queue_size'))

    def create_queue_consumer():
        process_args = (queue, beaver_config, file_config, logger)
        proc = multiprocessing.Process(target=run_queue, args=process_args)

        logger.info("Starting queue consumer")
        proc.start()
        return proc

    while 1:
        try:
            if REOPEN_FILES:
                logger.debug("Detected non-linux platform. Files will be reopened for tailing")

            logger.info("Starting worker...")
            worker = Worker(beaver_config, file_config, queue_consumer_function=create_queue_consumer, callback=queue.put, logger=logger)

            logger.info("Working...")
            worker.loop()

        except KeyboardInterrupt:
            logger.info("Shutting down. Please wait.")
            worker.close()
            if ssh_tunnel is not None:
                logger.info("Closing ssh tunnel.")
                ssh_tunnel.close()

            logger.info("Shutdown complete.")
            sys.exit(0)
