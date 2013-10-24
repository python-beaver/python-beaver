.. _install:

Installation
============

This part of the documentation covers the installation of Beaver.
The first step to using any software package is getting it properly installed.

Requirements
------------

* Python 2.6+
* Optional zeromq support: install libzmq (``brew install zmq`` or ``apt-get install libzmq-dev``) and pyzmq (``pip install pyzmq==2.1.11``)

Distribute & Pip
----------------

Installing Beaver is simple with `pip <http://www.pip-installer.org/>`_::

    $ pip install beaver

or, with `easy_install <http://pypi.python.org/pypi/setuptools>`_::

    $ easy_install beaver

But, you really `shouldn't do that <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_.

Cheeseshop (PyPI) Mirror
------------------------

If the Cheeseshop (a.k.a. PyPI) is down, you can also install Beaver from one
of the mirrors. `Crate.io <http://crate.io>`_ is one of them::

    $ pip install -i http://simple.crate.io/ beaver


Get the Code
------------

Beaver is actively developed on GitHub, where the code is
`always available <https://github.com/josegonzalez/beaver>`_.

You can either clone the public repository::

    git clone git://github.com/josegonzalez/beaver.git

Download the `tarball <https://github.com/josegonzalez/beaver/tarball/master>`_::

    $ curl -OL https://github.com/josegonzalez/beaver/tarball/master

Or, download the `zipball <https://github.com/josegonzalez/beaver/zipball/master>`_::

    $ curl -OL https://github.com/josegonzalez/beaver/zipball/master


Once you have a copy of the source, you can embed it in your Python package,
or install it into your site-packages easily::

    $ python setup.py install
