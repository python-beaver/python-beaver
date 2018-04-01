# -*- coding: utf-8 -*-
import multiprocessing
import Queue
import signal
import os
import time

from beaver.config import BeaverConfig
from beaver.run_queue import run_queue
from beaver.ssh_tunnel import create_ssh_tunnel
from beaver.utils import REOPEN_FILES, setup_custom_logger
from beaver.worker.tail_manager import TailManager

class TailRunner(object):
    def __init__(self, args):
        self.logger = setup_custom_logger('beaver', args)
        self.beaver_config = BeaverConfig(args, logger=self.logger)

        # so the config file can override the logger
        self.logger = setup_custom_logger('beaver', args, config=self.beaver_config)

        if self.beaver_config.get('logstash_version') not in [0, 1]:
            raise LookupError("Invalid logstash_version")

        self.queue = multiprocessing.Queue(self.beaver_config.get('max_queue_size'))

        self.manager_proc = None
        self.ssh_tunnel = create_ssh_tunnel(self.beaver_config)
        signal.signal(signal.SIGTERM, self.cleanup)
        signal.signal(signal.SIGINT, self.cleanup)
        if os.name != 'nt':
            signal.signal(signal.SIGQUIT, self.cleanup)

    def __getstate__(self):
        orig_dict = self.__dict__.copy()
        orig_dict['logger'] = self.logger.name
        return orig_dict

    def __setstate__(self, orig_dict):
        self.__dict__.update(orig_dict)
        self.logger = setup_custom_logger(orig_dict['logger'])

    def queue_put(*args):
        return self.queue.put(*args)

    def queue_put_nowait(*args):
        return self.queue.put_nowait(*args)

    def cleanup(signalnum, frame):
        if signalnum is not None:
            sig_name = tuple((v) for v, k in signal.__dict__.iteritems() if k == signalnum)[0]
            self.logger.info("{0} detected".format(sig_name))
            self.logger.info("Shutting down. Please wait...")
        else:
            self.logger.info('Worker process cleanup in progress...')

        try:
            self.queue_put_nowait(("exit", ()))
        except Queue.Full:
            pass

        if self.manager_proc is not None:
            try:
                self.manager_proc.terminate()
                self.manager_proc.join()
            except RuntimeError:
                pass

        if self.ssh_tunnel is not None:
            self.logger.info("Closing ssh tunnel...")
            self.ssh_tunnel.close()

        if signalnum is not None:
            self.logger.info("Shutdown complete.")
            return os._exit(signalnum)


    def create_queue_consumer():
        process_args = (self.queue, self.beaver_config, self.logger.name)
        proc = multiprocessing.Process(target=run_queue, args=process_args)

        self.logger.info("Starting queue consumer")
        proc.start()
        return proc

    def create_queue_producer():
        manager = TailManager(
            beaver_config=self.beaver_config,
            queue_consumer_function=self.create_queue_consumer,
            callback=self.queue_put,
            logger=self.logger
        )
        manager.run()

    def run(self):
        while 1:
            try:
                if REOPEN_FILES:
                    self.logger.debug("Detected non-linux platform. Files will be reopened for tailing")

                t = time.time()
                while True:
                    if self.manager_proc is None or not self.manager_proc.is_alive():
                        self.logger.info('Starting worker...')
                        t = time.time()
                        self.manager_proc = multiprocessing.Process(target=self.create_queue_producer)
                        self.manager_proc.start()
                        self.logger.info('Working...')
                    self.manager_proc.join(10)

                    if self.beaver_config.get('refresh_worker_process'):
                        if self.beaver_config.get('refresh_worker_process') < time.time() - t:
                            self.logger.info('Worker has exceeded refresh limit. Terminating process...')
                            self.cleanup(None, None)
            except KeyboardInterrupt:
                pass
