.. :changelog:

Changes
-------

9 (2012-11-28)
++++++++++++++

- Fixed deprecated warning when declaring exchange type
- More release script changes

8 (2012-11-28)
++++++++++++++

- Added connection exception trapping code
- Fixed release script

7 (2012-11-28)
++++++++++++++

- Partial fix for crashes caused by globbed files
- Added a helper script for creating releases

6 (2012-11-26)
++++++++++++++

- Fix issue where polling for files was done incorrectly
- Added ubuntu init.d example config

5 (2012-11-25)
++++++++++++++

- Try to poll for files on startup instead of throwing exceptions

4 (2012-11-25)
++++++++++++++

- Added argparse as a requirement for systems without argparse installed
- Relaxed pika version requirements
- Added python 2.6 support
- PEP8 Formatting
- Allow rabbitmq exchange type and durability to be configured

3 (2012-11-24)
++++++++++++++

- Changed lpush to rpush on redis transport
- Added udp support
- Updated timestamp in ISO 8601 format with the "Z" suffix to express UTC
- Zeromq installation is now optional
- Removed redundant README.txt
- Added classifiers to package
- Added example supervisor config file
- Added example bash startup file

2 (2012-10-25)
++++++++++++++

- Updated documentation
- Added support for ``config.ini`` based option parsing
- Refactored transports into separate files
- Added support for file globbing in paths
- Added msgpack and regular string output
- Force UTC time when ingesting logs
- Refactored logging to use the Python Logging Framework
- Added RabbitMQ support

1 (2012-08-05)
++++++++++++++

- Initial release
