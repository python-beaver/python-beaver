======
Beaver
======

.. image:: https://travis-ci.org/python-beaver/python-beaver.svg?branch=master
    :target: https://travis-ci.org/python-beaver/python-beaver

.. image:: https://coveralls.io/repos/python-beaver/python-beaver/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/python-beaver/python-beaver?branch=master

python daemon that munches on logs and sends their contents to logstash

Requirements
============

* Python 2.6+
* Optional zeromq support: install libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``) and pyzmq (``pip install pyzmq==2.1.11``)

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/python-beaver/python-beaver.git@36.2.0#egg=beaver

From PyPI::

    pip install beaver==36.2.0

Documentation
=============

Full documentation is available online at http://python-beaver.readthedocs.org/

You can also build the docs locally::

    # get sphinx installed
    pip install sphinx

    # retrieve the repository
    git clone git://github.com/python-beaver/beaver.git

    # build the html output
    cd beaver/docs
    make html

HTML docs will be available in `beaver/docs/_build/html`.

Contributing
============

When contributing to Beaver, please review the full guidelines here: https://github.com/python-beaver/python-beaver/blob/master/CONTRIBUTING.rst.
If you would like, you can open an issue to let others know about your work in progress. Documentation must be included and tests must pass on Python 2.6 and 2.7 for pull requests to be accepted.

Credits
=======

Based on work from Giampaolo and Lusis::

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
