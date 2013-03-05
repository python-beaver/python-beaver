import os
import signal
import subprocess
import time


def create_ssh_tunnel(beaver_config, logger=None):
    """Returns a BeaverSshTunnel object if the current config requires us to"""
    if not beaver_config.use_ssh_tunnel():
        return None

    logger.info("Proxying transport using through local ssh tunnel")
    return BeaverSshTunnel(beaver_config)


class BeaverSubprocess(object):
    """General purpose subprocess wrapper"""

    def __init__(self, beaver_config):
        """Child classes should build a subprocess via the following method:

           self._subprocess = subprocess.Popen(cmd, stdout=subprocess.PIPE, preexec_fn=os.setsid)

        This will allow us to attach a session id to the spawned child, allowing
        us to send a SIGTERM to the process on close
        """
        self._beaver_config = beaver_config
        self._subprocess = None

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

    def __init__(self, beaver_config):
        super(BeaverSshTunnel, self).__init__(beaver_config)

        key_file = beaver_config.get('ssh_key_file')
        tunnel = beaver_config.get('ssh_tunnel')
        tunnel_port = beaver_config.get('ssh_tunnel_port')
        remote_host = beaver_config.get('ssh_remote_host')
        remote_port = beaver_config.get('ssh_remote_port')

        self._subprocess = subprocess.Popen(["ssh", "-i", key_file, "-f", tunnel, "-L",
            "{0}:{1}:{2}".format(tunnel_port, remote_host, remote_port),
            "sleep 5"], stdout=subprocess.PIPE, preexec_fn=os.setsid)
        self.poll()
