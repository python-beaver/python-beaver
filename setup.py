#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2012 Jose Diaz-Gonzalez

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys

from beaver import __version__

try:
    from setuptools import setup
    setup  # workaround for pyflakes issue #13
except ImportError:
    from distutils.core import setup

# Hack to prevent stupid TypeError: 'NoneType' object is not callable error on
# exit of python setup.py test # in multiprocessing/util.py _exit_function when
# running python setup.py test (see
# http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html)
try:
    import multiprocessing
    multiprocessing
except ImportError:
    pass

requirements = open('requirements/base.txt').readlines()
if sys.version_info[:2] <= (2, 6):
    requirements.extend(open('requirements/base26.txt').readlines())

# python-daemon is not supported on windows
if sys.platform == 'win32':
    pd = filter(lambda r: r.startswith('python-daemon'), requirements)[0]
    requirements.remove(pd)

setup(
    name='Beaver',
    version=__version__,
    author='Jose Diaz-Gonzalez',
    author_email='email@josediazgonzalez.com',
    packages=[
        'beaver',
        'beaver.dispatcher',
        'beaver.tests',
        'beaver.transports',
        'beaver.worker'
    ],
    scripts=['bin/beaver'],
    url='http://github.com/josegonzalez/beaver',
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Logging',
    ],
    description='python daemon that munches on logs and sends their contents to logstash',
    long_description=open('README.rst').read() + '\n\n' +
                open('CHANGES.rst').read(),
    tests_require=open('requirements/tests.txt').readlines(),
    test_suite='nose.collector',
    install_requires=requirements, requires=['six']
)
