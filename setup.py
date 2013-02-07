#!/usr/bin/env python
import sys

from beaver import __version__

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.version_info[:2] <= (2, 6):
    requirements = open('requirements/base26.txt').readlines()
else:
    requirements = open('requirements/base.txt').readlines()

setup(
    name='Beaver',
    version=__version__,
    author='Jose Diaz-Gonzalez',
    author_email='support@savant.be',
    packages=['beaver', 'beaver.tests'],
    scripts=['bin/beaver'],
    url='http://github.com/josegonzalez/beaver',
    license=open('LICENSE.txt').read(),
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
    tests_require=['nose', 'mock', 'fakeredis'],
    test_suite='nose.collector',
    install_requires=requirements,
)
