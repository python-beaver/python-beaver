import datetime


def log(line):
        """Log a single line"""
        print "[{0}] {1}".format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), line)
