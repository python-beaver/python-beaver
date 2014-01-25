.. image:: https://secure.travis-ci.org/josegonzalez/beaver.png

======
Beaver
======

python daemon that munches on logs and sends their contents to logstash

Requirements
============

* Python 2.6+
* Optional zeromq support: install libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``) and pyzmq (``pip install pyzmq==2.1.11``)

Installation
============

Using PIP:

From Github::

    pip install git+git://github.com/josegonzalez/beaver.git#egg=beaver

From PyPI::

    pip install beaver==31

Documentation
=============

Full documentation is available online at http://beaver.readthedocs.org/

You can also build the docs locally:

    # get sphinx installed
    pip install sphinx

    # retrieve the repository
    git clone git://github.com/josegonzalez/beaver.git

    # build the html output
    cd beaver/docs
    make html

HTML docs will be available in `beaver/docs/_build/html`.

Credits
=======

Based on work from Giampaolo and Lusis::

    Real time log files watcher supporting log rotation.

    Original Author: Giampaolo Rodola' <g.rodola [AT] gmail [DOT] com>
    http://code.activestate.com/recipes/577968-log-watcher-tail-f-log/

    License: MIT

    Other hacks (ZMQ, JSON, optparse, ...): lusis
