#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='beaver',
    version='9',
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
    tests_require=["nose",],
    test_suite="nose.collector",
    install_requires=[
        "argparse>=1.2.0",
        "pika>=0.9.5",
        "redis==2.4.11",
        "ujson==1.9",
    ],
)
