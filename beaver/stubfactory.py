# -*- coding: utf-8 -*-
"""
Beaver RPC server factory
"""
from adminsocket import UnixAdminSocket
from beaverctlstub import BeaverctlServerStub, BeaverctlClientStub


class StubFactory(object):
    """
    Responsible for instantiation of beaverctl_stubs.
    """
    #TODO: MAKE PATH CONFIGURABLE VIA CONFIG FILE
    @staticmethod
    def create_beaverctl_server(dispatcher=False, s_dir):
        """Creates a stub using the admin socket provided"""
        #grab socket dir from config files
        admin_socket = UnixAdminSocket(s_dir)
        server = BeaverctlServerStub(admin_socket, dispatcher)
        return server

    @staticmethod
    def create_beaverctl_client(s_dir):
        """Create Beaverctl client stub"""
        #grab socket dir from config files
        client_socket = UnixAdminSocket(s_dir)
        client = BeaverctlClientStub(client_socket)
        return client
