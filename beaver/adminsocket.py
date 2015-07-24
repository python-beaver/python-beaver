# -*- coding: utf-8 -*-
"""
Administration socket
"""

import os
import abc
import socket
import pdb

class AdminSocket(object):
    """
    Creates a socket to allow communication between control utilities and a
    running beaver instance.  This provides the transport layer only higher
    level protocols are layered on top
    """


    MAX_MSG_LEN = 4096

    def __init__(self, path):
        """Set common class variables for client and server"""
        self.path = path
        #TODO: possibly make configurable via config file
        self._timeout = 10

    @abc.abstractmethod
    def create(self):
        """Create the admin socket"""
        raise RuntimeError('AdminSocket.create unimplemented')

    @abc.abstractmethod
    def destroy(self):
        """Delete the admin socket"""
        raise RuntimeError('AdminSocket.destroy unimplemented')

    @abc.abstractmethod
    def accept(self):
        """Accept incoming connection and return the connection"""
        raise RuntimeError('AdminSocket.accept unimplemented')

    @abc.abstractmethod
    def send(self, msg=None, conn=None):
        """Send a message to the peer"""
        raise RuntimeError('AdminSocket.send unimplemented')

    @abc.abstractmethod
    def receive(self, conn):
        """Receive a message from the peer"""
        raise RuntimeError('AdminSocket.recieve unimplemented')

    @abc.abstractmethod
    def connect(self):
        """Connect to the admin socket"""
        raise RuntimeError('AdminSocket.connect unimplemented')

    @abc.abstractmethod
    def disconnect(self):
        """Disconnect from the admin socket"""
        raise RuntimeError('AdminSocket.disconnect unimplemented')

    @abc.abstractmethod 
    def set_timeout(self, timeout):
        """Set timeout on socket connection"""
        raise RuntimeError('AdminSocket.set_timeout unimplemented')


class UnixAdminSocket(AdminSocket):
    """
    UNIX admin socket concrete type
    """

    def __init__(self, path):
        """Initialise UNIX socket instance variables"""
        super(UnixAdminSocket, self).__init__(path)
        # Socket object, False if not created
        self.socket = False

    def create(self):
        """Creates and binds to UNIX socket"""
        # Already open and bound, raise an error
        if self.socket:
            raise RuntimeError("Admin socket already created")
        # First run, make the directory structure
        directory = os.path.dirname(self.path)
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
            except OSError:
                raise RuntimeError('Unable to create run directory: '
                                   'check file permissions')
        # Check to see if an old socket already exists and clean it out
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                raise RuntimeError('Unable to remove existing socket: '
                                   'check file permissions')
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.bind(self.path)

    def destroy(self):
        """Close and destroy  UNIX Admin socket"""
        if not self.socket:
            raise RuntimeError('Admin socket not created')
        self.socket.close()
        self.socket = False
        #remove socket file
        if os.path.exists(self.path):
            try:
                os.remove(self.path)
            except OSError:
                raise RuntimeError('Unable to remove Admin Socket'
                                   'check file permissions')

    def listen(self):
        """Listen for connections on a UNIX socket"""
        if not self.socket:
            raise RuntimeError('Admin soccket not create')
        return self.socket.listen(1)

    def accept(self):
        """Accept connections on a UNIX socket"""
        if not self.socket:
            raise RuntimeError('Admin socket not created')
        return self.socket.accept()

    def send(self, conn=None, msg=None):
        """Send message over UNIX socket"""
        #TODO: add sending loop to ensure MAX_MSG_SIZE is sent
        if not self.socket:
            raise RuntimeError("Socket has not been created")
        if not conn:
            return self.socket.send(msg)
        return conn.send(msg)

    def receive(self, conn):
        """Receive message over UNIX socket"""
        #TODO: Add better receive method to ensure MAX_MSG_SIZE is received
        if not self.socket:
            raise RuntimeError("Socket has not been created")
        #pdb.set_trace()
        if not conn:
            return self.socket.recv(self.MAX_MSG_LEN)
        return conn.recv(self.MAX_MSG_LEN)

    def connect(self):
        """Client connect to socket created by server"""
        if self.socket:
            raise RuntimeError("Client Socket already created and connected")
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.settimeout(self._timeout)
        # Check to see if socket exists
        if not os.path.exists(self.path):
            raise RuntimeError("Admin Socket cannot be found at: " + self.path)
        try:
            self.socket.connect(self.path)
        except socket.error:
            raise RuntimeError("Unable to connect to socket: ")
 
    def disconnect(self):
        """Disconnects from Admin socket"""
        if not self.socket:
            raise RuntimeError("Client socket not created")
        self.socket.close()
        self.socket = False

    def set_timeout(self, timeout):
        self.socket.settimeout(timeout)

# vi: ts=4 et:
