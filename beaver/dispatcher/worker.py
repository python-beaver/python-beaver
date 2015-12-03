# -*- coding: utf-8 -*-
import multiprocessing
import Queue
import signal
import os
import time
import threading

from beaver.config import BeaverConfig
from beaver.runqueue import RunQueue
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.utils import setup_custom_logger, REOPEN_FILES
from beaver.worker.worker import Worker
from beaver.stubfactory import StubFactory


def run(args=None):
    """Main control process, creates managing processes,
    and starts run queue"""

    logger = setup_custom_logger('beaver', args)
    beaver_config = BeaverConfig(args, logger=logger)
    # so the config file can override the logger
    logger = setup_custom_logger('beaver', args, config=beaver_config)

    beaverctl_socket_path = beaver_config.get('beaverctl_socket_path')

    if beaver_config.get('logstash_version') not in [0, 1]:
        raise LookupError(
                "Invalid logstash_version. Set it to 0 or 1 in your config.")

    queue = multiprocessing.Queue(beaver_config.get('max_queue_size'))

    beaverctl = StubFactory.create_beaverctl_server(s_dir=beaverctl_socket_path)
    beaverctl_thread = threading.Thread(target=beaverctl.start_service_loop)

    worker_proc = None

    ssh_tunnel = create_ssh_tunnel(beaver_config, logger=logger)

    def cleanup(signalnum, frame):
        """Clean up resources"""
        if signalnum is not None:
            sig_name = \
                tuple((v) for v, k in signal.__dict__.iteritems() \
                if k == signalnum)[0]
            logger.info('{0} detected'.format(sig_name))
            logger.info('Shutting down. Please wait...')
        else:
            logger.info('Worker process cleanup in progress...')

        try:
            queue.put_nowait(('exit', ()))
        except Queue.Full:
            pass

        if worker_proc is not None:
            try:
                beaverctl.stop_service_loop()
                beaverctl_thread.join()

                worker_proc.terminate()
                worker_proc.join()
            except RuntimeError:
                pass

        if ssh_tunnel is not None:
            logger.info('Closing ssh tunnel...')
            ssh_tunnel.close()

        if signalnum is not None:
            logger.info('Shutdown complete.')
            return os._exit(signalnum)

    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGQUIT, cleanup)

    def create_queue_consumer():
        """Create queue consumer and Beaverctl"""
        run_queue = RunQueue(queue, beaver_config, logger)
        proc = multiprocessing.Process(target=run_queue.loop)
        beaverctl.set_dispatcher(run_queue)

        if not beaverctl_thread.is_alive():
            beaverctl_thread.start()

        logger.info('Starting queue consumer')
        proc.start()
        return proc

    def create_queue_producer():
        """creats and runs queue consumer"""
        worker = Worker(
		beaver_config, 
		queue_consumer_function=create_queue_consumer,
		callback=queue.put,
		logger=logger)
        worker.loop()

    while 1:
        try:
            if REOPEN_FILES:
                logger.debug('Detected non-linux platform.' \
                        ' Files will be reopened for tailing')

            t_taken = time.time()
            while True:
                if worker_proc is None or not worker_proc.is_alive():
                    logger.info('Starting worker...')
                    t_taken = time.time()
                    worker_proc = \
                        multiprocessing.Process(target=create_queue_producer)
                    worker_proc.start()
                    logger.info('Working...')
                worker_proc.join(10)

                if beaver_config.get('refresh_worker_process'):
                    if beaver_config.get('refresh_worker_process') \
		    < time.time() - t_taken:
                        logger.info('Worker has exceeded refresh limit.'
                                ' Terminating process...')
                        cleanup(None, None)

        except KeyboardInterrupt:
            pass
