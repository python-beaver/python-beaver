.. _caveats:

Caveats
=======

File tailing and shipping has a number of important issues that you should be aware of. These issues may affect just Beaver, or may affect other tools as well.

Copytruncate
------------

When using ``copytruncate`` style log rotation, two race conditions can occur:

1. Any log data written prior to truncation which Beaver has not yet
   read and processed is lost. Nothing we can do about that.

2. Should the file be truncated, rewritten, and end up being larger than
   the original file during the sleep interval, Beaver won't detect
   this. After some experimentation, this behavior also exists in GNU
   tail, so I'm going to call this a "don't do that then" bug :)

   Additionally, the files Beaver will most likely be called upon to
   watch which may be truncated are generally going to be large enough
   and slow-filling enough that this won't crop up in the wild.

FreeBSD
-------

When you get an error similar to ``ImportError: No module named
_sqlite3`` your python seems to miss the sqlite3-module. This can be the
case on FreeBSD and probably other systems. If so, use the local package
manager or port system to build that module. On FreeBSD::

    cd /usr/ports/databases/py-sqlite3
    sudo make install clean

Binary Log Data
---------------

Binary data in your logs will be converted to escape sequences or ?'s depending on the encoding settings to prevent decoding exceptions from crashing Beaver.

   | http://docs.python.org/2/library/codecs.html#codecs.replace_errors
   | malformed data is replaced with a suitable replacement character such as '?' in bytestrings and '\ufffd' in Unicode  strings.
