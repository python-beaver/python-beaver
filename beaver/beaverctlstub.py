# -*- coding: utf-8 -*-

"""
Beaver Control stub
"""
import adminsocket
import pickle
import signal
import socket
import abc
try:
    import cPickle as pickle
except:
    import pickle

class BeaverctlStub(object):
    """
    Creates RPC stub, providing proxy from which clients may send and receive
    remote procedure calls. Makes use of lower level communication protocols
    provided via AdminSocket interface.
    Handles requests and make procedure calls.
    """

    def __init__(self, socket):
        """Set common class variables for both client and server stubs"""
        self._socket = socket

    @abc.abstractmethod
    def close(self):
        """stop running loop and kill socket connection"""
        raise RuntimeError("Error BeaverctlStub.close unimplemented")



class BeaverctlServerStub(BeaverctlStub):
    """
    Create and maintains RPC connection for
    """

    def __init__(self, admin_socket, dispatcher=False):

        """Desc:
            Set adminsocket as class instance variable

            Arguments:
            (dispatcher) @object:
                Object to call methods on

            (admin_socket) @socket:
                handles transport
        """
        super(BeaverctlServerStub, self).__init__(admin_socket)
        self._dispatcher = dispatcher
        self._running = False
        self._timeout = 5
        signal.signal(signal.SIGTERM, self.stop_service_loop)

    def dispatch(self, method):
        """Dispatch method to server to object"""
        response = Response("NO OP")
        if not hasattr(self._dispatcher, str(method)):
            response = self.__invalid_operation()
        else:
            print "NO OP " + method
            print method
            response = self.__call_method(str(method))
        return response

    def __call_method(self, method):
        """calls method `method` from `dispatcher`"""
        try:
            ret = getattr(self._dispatcher, str(method))
        except Exception, e:
            print "ERROR"
            return Response(str(e), error=True)    
        return Response(str(ret()))

    def __noop(self, conn):
        """Perform no operation and return no op response object"""
        response = Response("There are no available operations", error=True)
        self._socket.send(conn,
                pickle.dumps(response, pickle.HIGHEST_PROTOCOL))

    def __invalid_operation(self):
        """Called when requested operation does not exist"""
        return Response("Invalid Operation", error=True)

    def service_loop(self):
        """Service loop, handles requests, and replies with return value"""
        self._running = True
        self._socket.create()
        self._socket.set_timeout(self._timeout)
        while self._running:
            try:
                conn = False
                self._socket.listen()
                conn, addr = self._socket.accept()
                if not conn:
                    raise RuntimeError("RPC Socket connection broken")
                request = self._socket.receive(conn)
                #TODO: better handle for invalid obj
                if not self._dispatcher:
                    self.__noop(conn)
                    continue
                response = self.dispatch(request)
                self._socket.send(conn,
                        pickle.dumps(response, pickle.HIGHEST_PROTOCOL))
                conn.close()
            except socket.timeout:
                continue
        return #kill loop

    def start_service_loop(self):
        """Starts main service loop"""
        self._running = True
        self._socket.create()
        self._socket.set_timeout(self._timeout)
        self.__service_loop()

    def stop_service_loop(self):
        """Set running to false, and destroy socket"""
        self._running = False
        self._socket.destroy()

    def close(self):
        """calls stop_service_loop"""
        self.stop_service_loop()

    def is_running(self):
        """Returns bool, is rpc server running"""
        return self._running

    def set_dispatcher(self, dispatcher_obj):
        """Sets the dispatcher object"""
        self._dispatcher = dispatcher_obj

    def remove_dispatcher(self):
        """Sets dispatcher to false and returns old dispatcher"""
        ret = self._dispatcher
        self._dispatcher = False
        return ret

class BeaverctlClientStub(BeaverctlStub):
    """
    Create and maintians RPC connection to RPC server
    """
    def __init__(self, connection_socket):
        """Set connectionSocket, as class instance variable"""
        super(BeaverctlClientStub, self).__init__(connection_socket)

    def make_remote_call(self, method):
        """Calls method 'method' passes 'params' and passes return
        back to callee"""
        response = None
        try:
            self._socket.connect()
            self._socket.set_timeout(5)
            self._socket.send(None, str(method))
            data = self._socket.receive(conn=None)
            try:
                response = pickle.loads(data)
            except pickle.PickleError:
                self.close()
                raise RuntimeError("Error unpickling reply")
            self._socket.disconnect()
            if response == None:
                raise RuntimeError("No Response received")
        except socket.timeout:
            response = Response("ERROR: Socket timed out", error = True)
        return response

    def close(self):
        self._socket.disconnect()

class Response(object):
    """
    Encapsulate procedure return value or error
    """

    def __init__(self, return_value, error=False):
        self._response = return_value
        self._error = error
        self._sent = False

    def set_response(self, ret_val):
        """Set response"""
        self._error = False
        self._response = ret_val

    def set_error(self, error):
        """Set error"""
        self._error = True
        self._response = error

    def get_response(self):
        """Get procedure return val, returns false, if there was an error"""
        if self._error:
            print "I HAVE ERROR" + self._error
            return self._error
        return self._response

    def get_error(self):
        """Get error message"""
        if self._error:
            return False
        return self._response
    
    def is_error(self):
        print "ERROR STTUS: " + str(self._error)
        if not self._error:
            return False
        return True
#vi: ts=4 et:
