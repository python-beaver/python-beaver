# -*- coding: utf-8 -*-
import multiprocessing
import Queue
import signal
import os

from beaver.config import BeaverConfig
from beaver.queue import run_queue
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.utils import REOPEN_FILES, setup_custom_logger
from beaver.worker.tail_manager import TailManager


def run(args=None):
    logger = setup_custom_logger('beaver', args)

    beaver_config = BeaverConfig(args, logger=logger)
    if beaver_config.get('logstash_version') not in [0, 1]:
        raise LookupError("Invalid logstash_version")

    queue = multiprocessing.JoinableQueue(beaver_config.get('max_queue_size'))

    manager = None
    ssh_tunnel = create_ssh_tunnel(beaver_config, logger=logger)

    def queue_put(*args):
        return queue.put(*args)

    def queue_put_nowait(*args):
        return queue.put_nowait(*args)

    def cleanup(signalnum, frame):
        sig_name = tuple((v) for v, k in signal.__dict__.iteritems() if k == signalnum)[0]
        logger.info("{0} detected".format(sig_name))
        logger.info("Shutting down. Please wait...")

        if manager is not None:
            logger.info("Closing worker...")
            try:
                manager.close()
            except RuntimeError:
                pass

        try:
            queue_put_nowait(("exit", ()))
        except Queue.Full:
            pass

        if ssh_tunnel is not None:
            logger.info("Closing ssh tunnel...")
            ssh_tunnel.close()

        logger.info("Shutdown complete.")
        return os._exit(signalnum)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGQUIT, cleanup)

    def create_queue_consumer():
        process_args = (queue, beaver_config, logger)
        proc = multiprocessing.Process(target=run_queue, args=process_args)

        logger.info("Starting queue consumer")
        proc.start()
        return proc

    if REOPEN_FILES:
        logger.debug("Detected non-linux platform. Files will be reopened for tailing")

    logger.info("Starting worker...")
    manager = TailManager(
        beaver_config=beaver_config,
        queue_consumer_function=create_queue_consumer,
        callback=queue_put,
        logger=logger
    )

    logger.info("Working...")
    manager.run()
