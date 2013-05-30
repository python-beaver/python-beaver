#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

setup(
    name='Beaver',
    version=__version__,
    author='Jose Diaz-Gonzalez',
    author_email='support@savant.be',
    packages=['beaver', 'beaver.dispatcher', 'beaver.tests', 'beaver.transports', 'beaver.worker'],
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
    install_requires=requirements,
)
