class Transport(object):

    def callback(self, filename, lines):
        return True

    def interrupt(self):
        return True

    def unhandled(self):
        return True
