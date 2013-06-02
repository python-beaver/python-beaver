# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import time

from beaver.base_log import BaseLog


def create_ssh_tunnel(beaver_config, logger=None):
    """Returns a BeaverSshTunnel object if the current config requires us to"""
    if not beaver_config.use_ssh_tunnel():
        return None

    logger.info("Proxying transport using through local ssh tunnel")
    return BeaverSshTunnel(beaver_config, logger=logger)


class BeaverSubprocess(BaseLog):
    """General purpose subprocess wrapper"""

    def __init__(self, beaver_config, logger=None):
        """Child classes should build a subprocess via the following method:

           self._subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)

        This will allow us to attach a session id to the spawned child, allowing
        us to send a SIGTERM to the process on close
        """
        super(BeaverSubprocess, self).__init__(logger=logger)
        self._log_template = '[BeaverSubprocess] - {0}'

        self._beaver_config = beaver_config
        self._command = 'sleep 1'
        self._subprocess = None
        self._logger = logger

    def run(self):
        self._log_debug('Running command: {0}'.format(self._command))
        self._subprocess = subprocess.Popen(['/bin/sh', '-c', self._command], preexec_fn=os.setsid)
        self.poll()

    def poll(self):
        """Poll attached subprocess until it is available"""
        if self._subprocess is not None:
            self._subprocess.poll()

        time.sleep(self._beaver_config.get('subprocess_poll_sleep'))

    def close(self):
        """Close child subprocess"""
        if self._subprocess is not None:
            os.killpg(self._subprocess.pid, signal.SIGTERM)
            self._subprocess = None


class BeaverSshTunnel(BeaverSubprocess):
    """SSH Tunnel Subprocess Wrapper"""

    def __init__(self, beaver_config, logger=None):
        super(BeaverSshTunnel, self).__init__(beaver_config, logger=logger)
        self._log_template = '[BeaverSshTunnel] - {0}'

        key_file = beaver_config.get('ssh_key_file')
        tunnel = beaver_config.get('ssh_tunnel')
        tunnel_port = beaver_config.get('ssh_tunnel_port')
        remote_host = beaver_config.get('ssh_remote_host')
        remote_port = beaver_config.get('ssh_remote_port')

        ssh_opts = []
        if self.get_port(tunnel):
            ssh_opts.append('-p {0}'.format(self.get_port(tunnel)))
            tunnel = self.get_host(tunnel)

        ssh_opts.append('-n')
        ssh_opts.append('-N')
        ssh_opts.append('-o BatchMode=yes')
        ssh_opts = ssh_opts + beaver_config.get('ssh_options')

        command = 'while true; do ssh {0} -i "{4}" "{5}" -L "{1}:{2}:{3}"; sleep 10; done'
        self._command = command.format(' '.join(ssh_opts), tunnel_port, remote_host, remote_port, key_file, tunnel)

        self.run()

    def get_host(self, tunnel=None):
        port = self.get_port(tunnel)
        if not port:
            return tunnel

        return tunnel[0:-(len(port) + 1)]

    def get_port(self, tunnel=None):
        host_port = None
        port = None

        if tunnel:
            host_port = tunnel.split('@')[-1]

        if host_port and len(host_port.split(':')) == 2:
            port = host_port.split(':')[-1]

        return port
