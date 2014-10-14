Changelog
=========

33.0.0 (2014-10-14)
-------------------

- Extend release script to support new, semver-tagged releases. [Jose
  Diaz-Gonzalez]

- Add gitchangelog.rc to fix changelog generation. [Jose Diaz-Gonzalez]

32 (2014-10-14)
---------------

- Merge pull request #267 from AeroNotix/gh-alf-allow-config-files-to-
  control-log-output. [Jose Diaz-Gonzalez]

  Allow for the config file to override the logfile's location

- Merge pull request #258 from PierreF/sincedb_write_interval. [Jose
  Diaz-Gonzalez]

  Fixed sincedb_write_interval (Bugs #229).

- Merge pull request #256 from svengerlach/ssh_options. [Jose Diaz-
  Gonzalez]

  fix config.get('ssh_options')

- Add debian packaging based on dh-virtualenv. [Jose Diaz-Gonzalez]

- Merge pull request #247 from fetep/zeromq-hwm-fix. [Jose Diaz-
  Gonzalez]

  zmq3 split HWM into SNDHWM/RCVHWM. Closes #246

- Merge pull request #242 from hltbra/patch-1. [Jose Diaz-Gonzalez]

  Fix typo in usage.rst

- Fixed badge to point to master branch only. [Jose Diaz-Gonzalez]

31 (2014-01-25)
---------------

- Add required spacing to readme for proper pypi doc support. [Jose
  Diaz-Gonzalez]

- Change release process to include processing of documentation. [Jose
  Diaz-Gonzalez]

- Merge pull request #239 from hltbra/master. [Jose Diaz-Gonzalez]

  Fix redis_transport.py redis exception handling. Fixes #238

- Merge pull request #237 from josegonzalez/call-close. [Jose Diaz-
  Gonzalez]

  Attempt to fix memory leaks. Closes #186

- Allow for newer versions of boto to be used. Closes #236. [Jose Diaz-
  Gonzalez]

- Merge pull request #230 from Runscope/master. [Jose Diaz-Gonzalez]

  When shipping logs, use millisecond
  precision timestamps.

- Merge pull request #228 from davidgarvey/master. [Jose Diaz-Gonzalez]

  Update config.py for python 2.6

- Improve compatibility with case-sensitive filesystems. [Jose Diaz-
  Gonzalez]

- Modify test cases to support logstash_version. [Jose Diaz-Gonzalez]

- Merge pull request #224 from pburkholder/logstash_version_help. [Jose
  Diaz-Gonzalez]

  Document usage of logstash_version

- Add add_field_env option to the config file to allow fields to be
  added using values from the environment. [Lance O'Connor]

  Closes #214

- Add SSL/TLS support to the RabbitMQ transport. Closes #217. [Jonathan
  Harker]

- Added http transport option. Closes #218. [Jeff Bryner]

- Merge pull request #223 from bearstech/initd. [Jose Diaz-Gonzalez]

  Fix: beaver user can't write its pid nor its log.

- Merge pull request #220 from ophelan/patch-1. [Jose Diaz-Gonzalez]

  Adding missing config file option 'rabbitmq_queue_durable'.

- `StrictRedis.from_url` is better than DIY-ing it. [Kristian Glass]

  Note currently `fakeredis` doesn't support `from_url`
  this is blocking
  on https://github.com/jamesls/fakeredis/pull/29 being merged in (I've
  bumped version requirement in `tests.txt` accordingly)

- Merge pull request #208 from tommyulfsparre/remove-non-string. [Jose
  Diaz-Gonzalez]

  Remove non string

- Merge pull request #206 from tommyulfsparre/skip-empty-input-object.
  [Jose Diaz-Gonzalez]

  Don't append empty strings

- Merge pull request #203 from chrisroberts/bugfix/lost-import-in-
  rebase-madness. [Jose Diaz-Gonzalez]

  Import threading library in tail manager since we want to use it

- Merge pull request #202 from moniker-dns/feature/add_ssl_support.
  [Jose Diaz-Gonzalez]

  Feature/add ssl support

- Redirect all docs to readthedocs. Refs #150. [Jose Diaz-Gonzalez]

- Readthedocs support. Closes #150. [Jose Diaz-Gonzalez]

- Merge pull request #199 from chrisroberts/enhancement/worker-process.
  [Jose Diaz-Gonzalez]

  Convert producer to process. Allow timed producer culling.

- Merge pull request #198 from chrisroberts/enhancement/no-wedgies.
  [Jose Diaz-Gonzalez]

  Make consumer check threaded to prevent wedge state

- Merge pull request #201 from atwardowski/master. [Jose Diaz-Gonzalez]

  Don't crash on a string decoding exception

- Merge pull request #197 from chrisroberts/bugfix/rabbitmq-revalid.
  [Jose Diaz-Gonzalez]

  Set transport as valid on connect (properly resets for reconnect)

- Merge pull request #195 from moniker-dns/feature/tcp-transport. [Jose
  Diaz-Gonzalez]

  Handle publication failures in the TCP transport correctly

- Add config option to manipulate ssh_options. [Andreas Lappe]

  This option allows to pass all ssh options to the tunnel.

- Merge pull request #194 from josegonzalez/logstash-format. [Jose Diaz-
  Gonzalez]

  Logstash format

- Merge pull request #193 from PierreF/multiline. [Jose Diaz-Gonzalez]

  Support for multi
  line events.

- Merge pull request #191 from LambdaDriver/master. [Jose Diaz-Gonzalez]

  Update README.rst

- Merge pull request #183 from reallyenglish/ignore_invalid_rawjson.
  [Jose Diaz-Gonzalez]

  ignore invalid rawjson log

- Merge pull request #181 from adesso-mobile/master. [Jose Diaz-
  Gonzalez]

  Deduplication of source host information

30 (2013-08-22)
---------------

- Merge pull request #179 from doismellburning/signal_handler_exit.
  [Jose Diaz-Gonzalez]

  Use os._exit over sys.exit in signal handlers to quit cleanly

- Merge pull request #165 from
  meekmichael/meekmichael/allow_string_escapes_in_delimiter. [Jose Diaz-
  Gonzalez]

  Allow string escapes in delimiter

- Merge pull request #153 from iyingchi/master. [Jose Diaz-Gonzalez]

  Added some missing confd docs

- Merge pull request #169 from jonathanq/master. [Jose Diaz-Gonzalez]

  Fixed example in Readme.rst for sqs_aws_secret_key

- Merge pull request #171 from romabysen/master. [Jose Diaz-Gonzalez]

  Allow path to be empty in configuration file.

- Merge pull request #159 from ohlol/master. [Jose Diaz-Gonzalez]

  Allow connecting or binding to multiple zmq addresses

- Merge pull request #168 from andrewgross/patch-1. [Jose Diaz-Gonzalez]

  Redis 2.4.11 is no longer available on Pypi

- Merge pull request #166 from moniker-dns/feature/tcp-transport. [Jose
  Diaz-Gonzalez]

  Add a TCP transport

- Merge pull request #161 from chrisroberts/fix/rabbitmq-reconnect.
  [Jose Diaz-Gonzalez]

  Add reconnect support for rabbitmq transport

- Corrected documentation for exclude tag. Closes #157. [Jose Diaz-
  Gonzalez]

- Merge pull request #155 from alappe/sqlite3_doc. [Jose Diaz-Gonzalez]

  Add missing sqlite3 module to documentation

- Merge pull request #154 from overplumbum/master. [Jose Diaz-Gonzalez]

  tests fix, travis
  ci integration

29 (2013-05-24)
---------------

- Do not harcode path in TailManager. Closes #143. [Jose Diaz-Gonzalez]

- Use /etc/beaver/conf for path and provide conf.d example. Closes #149.
  [Jose Diaz-Gonzalez]

- Added mqtt as option in argparse configuration for the transport flag.
  [Jose Diaz-Gonzalez]

- Fixed broken MqttTransport naming. [Jose Diaz-Gonzalez]

- Refactored BeaverSubprocess to maintain the running command as an
  attribute. [Jose Diaz-Gonzalez]

- Properly parse the beaver conf.d path for new sections. Closes #144.
  Closes #145. Refs #107. [Jose Diaz-Gonzalez]

- Use a Buffered Tokenizer to read large/fast incoming log input. Refs
  #135. Refs #105. [Jose Diaz-Gonzalez]

- Close queue after worker has been stopped. Refs #135. [Jose Diaz-
  Gonzalez]

- Wrap manager.close() call in try/except to mimic the worker
  dispatcher. [Jose Diaz-Gonzalez]

- Properly parse out the port from the `ssh_tunnel` option. Closes #142.
  [Jose Diaz-Gonzalez]

- Subclass the BaseLog class in BeaverSubprocess. Refs #142. [Jose Diaz-
  Gonzalez]

- Move base_log module higher up in hierarchy. Refs #142. [Jose Diaz-
  Gonzalez]

- Disable daemonization on the windows platform. Closes #141. [Jose
  Diaz-Gonzalez]

- Move file unwatching in old-style worker out of for-loop. Refs #139.
  [Jose Diaz-Gonzalez]

  Each worker has a `self._file_map` attribute which is a mapping of
  file ids to file data. When retrieving lines or checking on the status
  of the file, we use `iteritems()` which gives us a generator as
  opposed to a copy such as with `items()`. This generator allows us to
  iterate over the files without having issues where the file handle may
  open several times or other random Python issues.
  
  Using a generator also means that the set that we are iterating over
  should not change mid
  iteration, which it does if a file is unwatched. To circumvent this,
  we should use a separate list to keep track of files we need to
  unwatch or rewatch, and do it out of band.
  
  We should also take care to catch `RuntimeError` which may arise when
  closing the Worker out of band
  such as in the `cleanup` step of the worker dispatcher
  but nowhere else.
  
  This should fix issues where logrotate suddenly causes files to
  disappear for a time and beaver tries to tail the file at the exact
  time it is being recreated.

- Merge pull request #140 from jonathanq/master. [Jose Diaz-Gonzalez]

  Fixed a typo on the SQS docs

- Remove ujson requirement. [Jose Diaz-Gonzalez]

  This allows users that do not have a compiler in their deployment area
  to install beaver.
  
  Closes #137

- Turn on logfile output when running in non-daemon contexts. Closes
  #131. [Jose Diaz-Gonzalez]

- Expand logging output path. Closes #133. [Jose Diaz-Gonzalez]

- Ensure logging to a file does not destroy regular logging. Closes
  #132. [Jose Diaz-Gonzalez]

- Properly handle unreadable files by logging a warning instead of
  crashing. Closes #130. [Jose Diaz-Gonzalez]

- Rename null_formatter to raw_formatter in BaseTransport class. [Jose
  Diaz-Gonzalez]

- Ensure that the RedisTransport calls the super invalidate method. Refs
  #93. [Jose Diaz-Gonzalez]

- Fix issue where input type was not being detected properly. [Jose
  Diaz-Gonzalez]

- Use logfile flag for sending all output to a file in daemon contexts.
  [Jose Diaz-Gonzalez]

- Expand path for pidfile creation. [Jose Diaz-Gonzalez]

- Properly handle redis reconnects when the datastore becomes
  unreacheable. Refs #93. [Jose Diaz-Gonzalez]

- Merge pull request #129 from pchandra/master. [Jose Diaz-Gonzalez]

  Adding HA options for rabbitmq

- Respect stat_interval file configuration in stable worker. [Jose Diaz-
  Gonzalez]

- Unified configuration file using conf_d module. [Jose Diaz-Gonzalez]

  This change adds support for a conf.d directory
  configured only via the `
  
  confd
  path` flag
  which allows beaver to read configuration from multiple files.
  
  Please note that the primary `beaver` stanza MUST be located in the
  file specified by the `
  
  configfile` argument. Any other such `beaver` stanzas will be ignored.
  
  This change also unifies the `BeaverConfig` and `FileConfig` classes,
  and simplifies the api for retrieving global vs file
  specific data.
  
  Please note that this commit BREAKS custom transport classes, as the
  interface for creating a transport class has changed. If you are
  referencing a `file_config.get(field, filename)` anywhere, please omit
  this and refer to `beaver_config.get_field(field, filename)`.
  
  Closes #107

- Hack to prevent stupid TypeError: 'NoneType' when running tests via
  setup.py. [Jose Diaz-Gonzalez]

- Properly handle rotated files on Darwin architectures. [Jose Diaz-
  Gonzalez]

- Log to debug instead of warning for file reloading on Darwin
  architectures. [Jose Diaz-Gonzalez]

- Speed up experimental worker. [Jose Diaz-Gonzalez]

  Removed inline sleep call, which slowed down passes n*0.1 seconds,
  where n is the number of files being tailed
  
  Inline methods that update data structures which should speed up
  larger installations
  
  Make self.active() an attribute lookup instead of a method call

- Use latest version of message pack interface (0.3.0). Closes #128.
  [Jose Diaz-Gonzalez]

- Merge pull request #126 from jlambert121/120_fix. [Jose Diaz-Gonzalez]

  alternative for reading python requirements

- Fix options sent from original worker to queue. Refs #119. [Jose Diaz-
  Gonzalez]

- Allow users to ignore the results of a copytruncate from logrotate.
  Refs #105. [Jose Diaz-Gonzalez]

- Fix rpm package building. Closes #123. [Jose Diaz-Gonzalez]

- Added experimental tail-version of beaver. [Jose Diaz-Gonzalez]

- Beginning work to move from an omniscient worker to individual tail
  objects. [Jose Diaz-Gonzalez]

- Fix kwargs call. [Jose Diaz-Gonzalez]

- Add formatting to mqtt transport. Closes #115. [Jose Diaz-Gonzalez]

- Retrieve more data from callback to minimize dictionary lookups. [Jose
  Diaz-Gonzalez]

- Prefer single quotes to double quotes where possible. [Jose Diaz-
  Gonzalez]

- Ensure stat_interval and tail_lines are both integer values. [Jose
  Diaz-Gonzalez]

- Alphabetize config variables for file_config. [Jose Diaz-Gonzalez]

- Ensure that debug flag is a boolean. [Jose Diaz-Gonzalez]

- Follow logstash covention for 'format' instead of 'message_format'
  [Jose Diaz-Gonzalez]

- Use passed in 'ignore_empty' field instead of a file_config lookup in
  queue module. [Jose Diaz-Gonzalez]

- Prefer discover_interval over update_file_mapping_time. [Jose Diaz-
  Gonzalez]

- Fix TransportException import. Closes #122. [Jose Diaz-Gonzalez]

- Merge pull request #121 from amfranz/master. [Jose Diaz-Gonzalez]

  SSH tunnel is not re
  connecting

- Use an alternative method of reading in requirements. Refs #120. [Jose
  Diaz-Gonzalez]

- Fix import of REOPEN_FILES constant in dispatcher.py. [Jose Diaz-
  Gonzalez]

- Fix a PEP8 violation. [Jose Diaz-Gonzalez]

- Ensure all files are utf-8 encoded. [Jose Diaz-Gonzalez]

- Namespace transport classes in the transport module. [Jose Diaz-
  Gonzalez]

- Allow specifying debug mode via argument. [Jose Diaz-Gonzalez]

- Added thread-safety to datetime calls. [Jose Diaz-Gonzalez]

- Added support for message_format. Closes #91. [Jose Diaz-Gonzalez]

- Add msgpack_pure as fallback for C-Based msgpack package. [Jose Diaz-
  Gonzalez]

- Fix issues in sincedb implementation. Refs #116. [Jose Diaz-Gonzalez]

- Fix casting issue when checking start_position. [Jose Diaz-Gonzalez]

- Properly handle Queue.Full exceptions. [Jose Diaz-Gonzalez]

- More logging. [Jose Diaz-Gonzalez]

- Expand the sincedb path on configuration parse. [Jose Diaz-Gonzalez]

- Ignore since.db files. [Jose Diaz-Gonzalez]

- Simplified sincedb support to handle an edge case. Refs #116. [Jose
  Diaz-Gonzalez]

- Remove errant print. [Jose Diaz-Gonzalez]

- Added support for file exclusion in config stanzas. Closes #106. [Jose
  Diaz-Gonzalez]

- Added python regex exclusion support to eglob. Refs #106. [Jose Diaz-
  Gonzalez]

- PEP8. [Jose Diaz-Gonzalez]

- Added a tests directory with some sample tests from users. [Jose Diaz-
  Gonzalez]

- Convert the 'sincedb_write_interval' option to an integer. Refs #116.
  [Jose Diaz-Gonzalez]

- Moved logger call to a more intelligent spot. [Jose Diaz-Gonzalez]

- Ensure that we use the proper encoding when opening a file. Closes
  #104. [Jose Diaz-Gonzalez]

- Centralize file-reading using classmethod open() [Jose Diaz-Gonzalez]

- Fixed issue where tailed lines were not being properly sent to the
  callback. [Jose Diaz-Gonzalez]

- Remove unnecessary argument from Worke.__init__() [Jose Diaz-Gonzalez]

- Force-parse non-unicode files using unicode_dammit. [Jose Diaz-
  Gonzalez]

- Set utf-8 as default encoding on all python files. [Jose Diaz-
  Gonzalez]

- Fixed pyflakes issues. [rtoma]

- Syntax fix of list. [rtoma]

- Raise an AssertionError when run in daemon without a pid path
  specified. Closes #112. [Jose Diaz-Gonzalez]

- Add support for ignoring empty lines. [Jose Diaz-Gonzalez]

- Properly cast boolean values from strings. [Jose Diaz-Gonzalez]

- Ensure all sections have the proper values on start. [Jose Diaz-
  Gonzalez]

- Ensure internal file_config state is updated. [Jose Diaz-Gonzalez]

- Pass in timestamp from worker class for more accurate timestamps at
  the cost of speed of sending. [Jose Diaz-Gonzalez]

- Centralize timestamp retrieval to base transport class. [Jose Diaz-
  Gonzalez]

- Added support for gzipped files. refs #39. [Jose Diaz-Gonzalez]

- Added support for sqlite3-based sincedb. Refs #6 and #39. [Jose Diaz-
  Gonzalez]

- Refactored worker so as to allow further data to be added to the
  file_map. [Jose Diaz-Gonzalez]

- Refactor seek_to_end to properly support file tailing. [Jose Diaz-
  Gonzalez]

- Added support for pubsub zmq. [Jose Diaz-Gonzalez]

- Added support for mosquitto transport. [Jose Diaz-Gonzalez]

- Added support for specifying file encoding, using io.open vs os.open.
  [Jose Diaz-Gonzalez]

- Fix issue where a field may not exist in the data. [Jose Diaz-
  Gonzalez]

- Added support for rawjson format. [Jose Diaz-Gonzalez]

- Fixed zeromq tests. [Jose Diaz-Gonzalez]

- Added SQS transport. [Jonathan Quail]

- Merge pull request #109 from mdelagralfo/transport-docs. [Jose Diaz-
  Gonzalez]

  fixing outdated transport docs

28 (2013-03-05)
---------------

- BeaverSubprocess is now a new-style class. Fixes ssh_tunneling. [Jose
  Diaz-Gonzalez]

27 (2013-03-05)
---------------

- Fix issue where super method was not called in BeaverSshTunnel. [Jose
  Diaz-Gonzalez]

26 (2013-03-05)
---------------

- Add optional reconnect support for transports. Refs #93. [Jose Diaz-
  Gonzalez]

- Add a method for checking the validity of a Transport. Refs #93. [Jose
  Diaz-Gonzalez]

- Added a configurable subprocess poll sleep. [Jose Diaz-Gonzalez]

- Add a deafult sleep timeout to BeaverSubprocess polling. [Jose Diaz-
  Gonzalez]

- Use a larger sleep time to get around redis over ssh connection
  issues. [Jose Diaz-Gonzalez]

25 (2013-03-05)
---------------

- Use True instead of 1 for while check. [Jose Diaz-Gonzalez]

- Fix orphan child processes. Closes #103. [Jose Diaz-Gonzalez]

24 (2013-02-26)
---------------

- Ensure new files are added to a transports configuration. Closes #96.
  Closes #101. [Jose Diaz-Gonzalez]

- Allow float numbers for update_file_mapping_time. [Jose Diaz-Gonzalez]

- Fix invalid casting of boolean values. [Jose Diaz-Gonzalez]

- Perform all conversions in config.py. Closes #99. [Jose Diaz-Gonzalez]

- Merge pull request #102 from andrewgross/master. [Jose Diaz-Gonzalez]

  Clarify Docs

23 (2013-02-20)
---------------

- Merge pull request #100 from temoto/patch-1. [Jose Diaz-Gonzalez]

  worker: pretty format debug message "Iteration took %.6f"

- Merge pull request #98 from overplumbum/master. [Jose Diaz-Gonzalez]

  ZeroMq HighWaterMark socket option

- Merge pull request #95 from anentropic/custom_transports. [Jose Diaz-
  Gonzalez]

  allow beaver to accept custom transport classes

- Merge pull request #97 from onddo/README-exchange-type. [Jose Diaz-
  Gonzalez]

  rabbitmq_exchange_type option fixed in the README

- Merge pull request #94 from anentropic/zmq_test_fix. [Jose Diaz-
  Gonzalez]

  sort of fix the broken zmq test

22 (2013-01-15)
---------------

- Handle sigterm properly. Refs #87. [Jose Diaz-Gonzalez]

- Add --loglevel as alias for --output. Closes #92. [Jose Diaz-Gonzalez]

- Merge pull request #90 from Appdynamics/master. [Jose Diaz-Gonzalez]

  redis connection resiliency

- Merge pull request #89 from grncdr/no-formatting. [Jose Diaz-Gonzalez]

  Fix string & null formatter, add CLI option to use null formatter

- Call file.readlines() with sizehint in a loop to avoid reading in
  massive files all at once. [Jose Diaz-Gonzalez]

21 (2013-01-04)
---------------

- Move runner into a dispatcher class to solve installation issues.
  [Jose Diaz-Gonzalez]

- Added note for Python 2.6+ support. [Jose Diaz-Gonzalez]

20 (2013-01-03)
---------------

- Copy the readme over to avoid pypi packaging warnings. [Jose Diaz-
  Gonzalez]

- Merge pull request #84 from blt/fully_recursive_globbing. [Jose Diaz-
  Gonzalez]

  Implement fully recursive file globing.

19 (2013-01-01)
---------------

- Fix issue with supporting command line args. [Jose Diaz-Gonzalez]

18 (2012-12-31)
---------------

- Add timing debug information to the worker loop. [Jose Diaz-Gonzalez]

- Use redis pipelining when sending events. [Jose Diaz-Gonzalez]

- Formatting. [Jose Diaz-Gonzalez]

- Do not output debug statement for file_config.get call. [Jose Diaz-
  Gonzalez]

- Pass in logger object to create_ssh_tunnel() [Jose Diaz-Gonzalez]

- Merge pull request #83 from clarkbk/patch-1. [Jose Diaz-Gonzalez]

  Update .gitignore

17 (2012-12-28)
---------------

- Added missing python-daemon requirement. [Jose Diaz-Gonzalez]

16 (2012-12-27)
---------------

- Specify a max queue size of 100 to limit overrunning memory. [Jose
  Diaz-Gonzalez]

- Use multiprocessing for handling larger queue sizes. [Jose Diaz-
  Gonzalez]

  Previously there were issues where files that were updated frequently
  such as varnish or server logs
  would overwhelm the naive implementation of file.readlines() within
  Beaver. This would cause Beaver to slowly read larger and larger
  portions of a file before processing any of the lines, eventually
  causing Beaver to take forever to process log lines.
  
  This patch adds the ability to use an internal work queue for log
  lines. Whenever file.readlines() is called, the lines are placed in
  the queue, which is shared with a child process. The child process
  creates its own transport, allowing us to potentially create a Process
  Pool in the future to handle a larger queue size.
  
  Note that the limitation of file.readlines() reading in too many lines
  is still in existence, and may continue to cause issues for certain
  log files.

- Add default redis_password to BeaverConfig class. [Jose Diaz-Gonzalez]

- Merge pull request #81 from normanjoyner/master. [Jose Diaz-Gonzalez]

  Implement redis auth support

- Add beaver init script for daemonization mode. [Jose Diaz-Gonzalez]

- Use python logger when using StdoutTransport. [Jose Diaz-Gonzalez]

- Add short arg flags for hostname and format. [Jose Diaz-Gonzalez]

- Add the ability to daemonize. Closes #79. [Jose Diaz-Gonzalez]

- Pass around a logger instance to all transports. [Jose Diaz-Gonzalez]

- Revert "Added a lightweight Event class" [Jose Diaz-Gonzalez]

  After deliberation, beaver is meant to be "light
  weight". Lets leave
  the heavy
  hitting to the big
  boys.
  
  This reverts commit 1619d33ef4803c3fe910cf4ff197d0dd0039d2eb.

- Added a lightweight Event class. [Jose Diaz-Gonzalez]

  This class's sole responsibility will be the processing of a given
  line as an event.
  It's future goal will be to act as a lightweight implementation of the
  filter system within Logstash

- Remove argparse requirement for python 2.7 and above. [Jose Diaz-
  Gonzalez]

15 (2012-12-25)
---------------

- Pull argument parsing out of beaver __init__.py. [Jose Diaz-Gonzalez]

- Move app-running into __init__.py. [Jose Diaz-Gonzalez]

- Standardize on _parse() as method for parsing config. [Jose Diaz-
  Gonzalez]

- Automatically parse the path config option. [Jose Diaz-Gonzalez]

- Remove extensions argument on Worker class. [Jose Diaz-Gonzalez]

  This argument was only used when no globs were specified in a config
  file.
  Since it is not configurable, there is no sense leaving around the
  extra logic.

- Remove extra callback invocation on readlines. [Jose Diaz-Gonzalez]

- Remove extra file_config module. [Jose Diaz-Gonzalez]

- General code reorganization. [Jose Diaz-Gonzalez]

  Move both BeaverConfig and FileConfig into a single class
  
  Consolidated run_worker code with code in beaver binary file. This
  will create a clearer path for Exception handling, as it is now the
  responsibility of the calling class, allowing us to remove duplicative
  exception handling code.
  
  Added docstrings to many fuctions and methods
  
  Moved extra configuration and setup code to beaver.utils module. In
  many cases, code was added hastily before.
  
  Made many logger calls debug as opposed to info. The info level should
  be generally reserved for instances where files are watched,
  unwatched, or some change in the file state has occurred.

- Remove duplicative and old beaver instructions from binary. [Jose
  Diaz-Gonzalez]

- Remove unnecessary passing of ssh_tunnel subprocess. [Jose Diaz-
  Gonzalez]

- Added docstrings to ssh_tunnel module. [Jose Diaz-Gonzalez]

- Follow convention of underscore for object properties. [Jose Diaz-
  Gonzalez]

- Follow convention of underscore for object properties. [Jose Diaz-
  Gonzalez]

- Added a NullFormatter. [Jose Diaz-Gonzalez]

  Useful for cases where we do not want any extra overhead on message
  formatting

- Refactored message formatting in base Transport class. [Jose Diaz-
  Gonzalez]

  We now use a `_formatter` property on the Transport class which
  will properly process the message for output as the user expects.
  
  In the case of string output, we define a custom formatter using an
  anonymous function and specify that as the formatter.

- Moved create_transport to transport module. [Jose Diaz-Gonzalez]

- Moved create_ssh_tunnel to ssh_tunnel module. [Jose Diaz-Gonzalez]

- Fixed order of beaver_config and file_config in args. [Jose Diaz-
  Gonzalez]

- Reduce overhead of parsing configuration for globs and files. [Jose
  Diaz-Gonzalez]

- Removed ordereddict dependency. [Jose Diaz-Gonzalez]

- Do not output info level when outputing version. [Jose Diaz-Gonzalez]

- Allow usage of ujson >= 1.19. Closes #76. [Jose Diaz-Gonzalez]

14 (2012-12-18)
---------------

- Removed erroneous redundant code. [Jose Diaz-Gonzalez]

- Workaround for differing iteration implementation in Python 2.6. [Jose
  Diaz-Gonzalez]

- Properly detect non-linux platforms. [Jose Diaz-Gonzalez]

- Improve Python 2.6 support. [Jose Diaz-Gonzalez]

- Fix broken python readme. [Jose Diaz-Gonzalez]

13 (2012-12-17)
---------------

- Fixed certain environment variables. [Jose Diaz-Gonzalez]

- SSH Tunnel Support. [Jose Diaz-Gonzalez]

  This code should allow us to create an ssh tunnel between two distinct
  servers for the purposes of sending and receiving data.
  
  This is useful in certain cases where you would otherwise need to
  whitelist in your Firewall or iptables setup, such as when running in
  two different regions on AWS.

- Allow for initial connection lag. Helpful when waiting for an SSH
  proxy to connect. [Jose Diaz-Gonzalez]

- Fix issue where certain config defaults were of an improper value.
  [Jose Diaz-Gonzalez]

- Allow specifying host via flag. Closes #70. [Jose Diaz-Gonzalez]

12 (2012-12-17)
---------------

- Merge pull request #73 from josegonzalez/deprecated. [Jose Diaz-
  Gonzalez]

  Revamp Beaver configuration

- Minor changes for PEP8 conformance. [Jose Diaz-Gonzalez]

11 (2012-12-16)
---------------

- Merge pull request #69 from kitchen/fqdnoptional. [Jose Diaz-Gonzalez]

  add optional support for socket.getfqdn

- Merge pull request #67 from kitchen/truncate-check. [Jose Diaz-
  Gonzalez]

  check for truncation as well as rotation

- Add a version number to beaver. [Jose Diaz-Gonzalez]

10 (2012-12-15)
---------------

- Fixed package name. [Jose Diaz-Gonzalez]

- Regenerate CHANGES.rst on release. [Jose Diaz-Gonzalez]

- Merge pull request #66 from rckclmbr/eglob. [Jose Diaz-Gonzalez]

  Adding support for /path/{foo,bar}.log

- Merge pull request #61 from faulkner/fix-readme. [Jose Diaz-Gonzalez]

  Fix readme

- Merge pull request #65 from rckclmbr/nfsfix. [Jose Diaz-Gonzalez]

  Ignore file errors in unwatch method
  
  the file might not exists

- Merge pull request #64 from rckclmbr/master. [Jose Diaz-Gonzalez]

  Unwatch file when encountering a stale NFS handle.

- Merge pull request #63 from faulkner/fix-setup. [Jose Diaz-Gonzalez]

  Fix setup

- Merge pull request #59 from stelmod/master. [Jose Diaz-Gonzalez]

  Beaver sends empty string as tag

- Merge pull request #56 from rckclmbr/master. [Jose Diaz-Gonzalez]

  Making 'mode' option work for zmqtransport

9 (2012-11-28)
--------------

- More release changes. [Jose Diaz-Gonzalez]

- Merge pull request #53 from rafaelmagu/master. [Jose Diaz-Gonzalez]

  Fixed deprecation warning in rabbitmq_transport.py

8 (2012-11-28)
--------------

- Merge pull request #52 from rafaelmagu/master. [Jose Diaz-Gonzalez]

  Added resiliency to RabbitMQ transport

7 (2012-11-28)
--------------

- Added a helper script for creating releases. [Jose Diaz-Gonzalez]

- Partial fix for crashes caused by globbed files. [Jose Diaz-Gonzalez]

6 (2012-11-26)
--------------

- Fix issue where polling for files was done incorrectly. [Jose Diaz-
  Gonzalez]

- Added ubuntu init.d example config. [Jose Diaz-Gonzalez]

5 (2012-11-26)
--------------

- Try to poll for files on startup instead of throwing exceptions.
  Closes #45. [Jose Diaz-Gonzalez]

- Added python 2.6 to classifiers. [Jose Diaz-Gonzalez]

4 (2012-11-26)
--------------

- Remove unused local vars. [Jose Diaz-Gonzalez]

- Allow rabbitmq exchange type and durability to be configured. [Jose
  Diaz-Gonzalez]

- Remove unused import. [Jose Diaz-Gonzalez]

- Formatted code to fix PEP8 violations. [Jose Diaz-Gonzalez]

- Use alternate dict syntax for Python 2.6 support. Closes #43. [Jose
  Diaz-Gonzalez]

- Fixed release date for version 3. [Jose Diaz-Gonzalez]

3 (2012-11-25)
--------------

- Added requirements files to manifest. [Jose Diaz-Gonzalez]

- Include all contrib files in release. [Jose Diaz-Gonzalez]

- Revert "removed redundant README.txt" to follow pypi standards. [Jose
  Diaz-Gonzalez]

  This reverts commit e667f63706e0af8bc82c0eac6eac43318144e107.

- Added bash startup script. Closes #35. [Jose Diaz-Gonzalez]

- Added an example supervisor config for redis. closes #34. [Jose Diaz-
  Gonzalez]

- Removed redundant README.txt. [Jose Diaz-Gonzalez]

- Added classifiers to package. [Jose Diaz-Gonzalez]

- Re-order workers. [Jose Diaz-Gonzalez]

- Re-require pika. [Jose Diaz-Gonzalez]

- Make zeromq installation optional. [Morgan Delagrange]

- Formatting. [Jose Diaz-Gonzalez]

- Added changes to changelog for version 3. [Jose Diaz-Gonzalez]

- Merge pull request #41 from onddo/timezone-utc. [Jose Diaz-Gonzalez]

  timestamp in ISO 8601 format with the "Z" sufix to express UTC

- Merge pull request #40 from mdelagralfo/master. [Jose Diaz-Gonzalez]

  adding udp transport support

- Merge pull request #37 from onddo/redis-rpush. [Jose Diaz-Gonzalez]

  lpush changed to rpush on redis transport

2 (2012-10-25)
--------------

- Merge pull request #32 from michaeldauria/init-script. [Jose Diaz-
  Gonzalez]

  Example upstart script

- Fixed a few more import statements. [Jose Diaz-Gonzalez]

- Fixed binary call. [Jose Diaz-Gonzalez]

- Refactored logging. [Jose Diaz-Gonzalez]

- Improve logging. [Michael D'Auria]

- Removed unnecessary print statements. [Jose Diaz-Gonzalez]

- Add default stream handler when transport is stdout. Closes #26. [bear
  (Mike Taylor)]

- Merge pull request #30 from michaeldauria/better-unhandled-exception-
  output. [Jose Diaz-Gonzalez]

  Better exception handling for unhandled exceptions

- Merge pull request #29 from michaeldauria/fix-getaddfield. [Jose Diaz-
  Gonzalez]

  Handle the case where the config file is not present

- Merge pull request #25 from shaftoe/fixaddvalues. [Jose Diaz-Gonzalez]

  Fix wrong addfield values

- Add add_field to config example. [Alexander Fortin]

- Add support for add_field into config file. [Alexander Fortin]

- Minor readme updates. [Jose Diaz-Gonzalez]

- Merge pull request #21 from librato-peter/master. [Jose Diaz-Gonzalez]

  Fix so that empty file lists do not override the PATH.

- Add support for type reading from INI config file. [Alexander Fortin]

  Add support for symlinks in config file
  
  Add support for file globbing in config file
  
  Add support for tags
  
  
  a little bit of refactoring, move type and tags check down into
  transport class
  
  create config object (reading /dev/null) even if no config file
  has been given via cli
  
  Add documentation for INI file to readme
  
  Remove unused json library
  
  Conflicts:
  README.rst

- Merge pull request #17 from librato-peter/master. [Jose Diaz-Gonzalez]

  Updating docs for zmq transport method

- Merge pull request #13 from DazWorrall/globs. [Jose Diaz-Gonzalez]

  Support globs in file paths

- Merge pull request #14 from DazWorrall/utc. [Jose Diaz-Gonzalez]

  When sending data over the wire, use UTC timestamps

- Added msgpack support. [Jose Diaz-Gonzalez]

- Use the python logging framework. [Jose Diaz-Gonzalez]

- Fixed Transport.format() method. [Jose Diaz-Gonzalez]

- Properly parse BEAVER_FILES env var. [Jose Diaz-Gonzalez]

- Refactor transports. [Jose Diaz-Gonzalez]

  Fix the json import to use the fastest json module available
  
  Move formatting into Transport class

- Attempt to fix defaults from env variables. [Jose Diaz-Gonzalez]

- Merge pull request #8 from jdutton/master. [Jose Diaz-Gonzalez]

  Fixed typos in docs to reference RABBITMQ_HOST rather than
  RABBITMQ_ADDRESS

- Merge pull request #4 from shaftoe/master. [Jose Diaz-Gonzalez]

  Add RabbitMQ support

- Added real-world example of beaver usage for tailing a file. [Jose
  Diaz-Gonzalez]

- Removed unused argument. [Jose Diaz-Gonzalez]

- Ensure that python-compatible readme is included in package. [Jose
  Diaz-Gonzalez]

- Fix variable naming and timeout for redis transport. [Jose Diaz-
  Gonzalez]

- Installation instructions. [Jose Diaz-Gonzalez]

- Use restructured text for readme instead of markdown. [Jose Diaz-
  Gonzalez]

- Removed unnecessary .gitignore. [Jose Diaz-Gonzalez]

1 (2012-08-06)
--------------

- Moved app into python package format. [Jose Diaz-Gonzalez]

- Moved binary beaver.py to bin/beaver, as per python packaging. [Jose
  Diaz-Gonzalez]

- Moved around transports to be independent of each other. [Jose Diaz-
  Gonzalez]

- Reorder transports. [Jose Diaz-Gonzalez]

- Rewrote run_worker to throw exception if all transport options have
  been exhausted. [Jose Diaz-Gonzalez]

- Rename Amqp -> Zmq to avoid confusion with RabbitMQ. [Alexander
  Fortin]

- Added choices to the --transport argument. [Jose Diaz-Gonzalez]

- Fixed derpy formatting. [Jose Diaz-Gonzalez]

- Added usage to the readme. [Jose Diaz-Gonzalez]

- Support usage of environment variables instead of arguments. [Jose
  Diaz-Gonzalez]

- Fixed files argument parsing. [Jose Diaz-Gonzalez]

- One does not simply license all the things. [Jose Diaz-Gonzalez]

- Add todo to readme. [Jose Diaz-Gonzalez]

- Added version to pyzmq. [Jose Diaz-Gonzalez]

- Added license. [Jose Diaz-Gonzalez]

- Reordered imports. [Jose Diaz-Gonzalez]

- Moved all transports to beaver/transports.py. [Jose Diaz-Gonzalez]

- Calculate current timestamp at most once per callback fired. [Jose
  Diaz-Gonzalez]

- Modified transports to include proper information for ingestion in
  logstash. [Jose Diaz-Gonzalez]

- Fixed package imports. [Jose Diaz-Gonzalez]

- Removed another compiled python file. [Jose Diaz-Gonzalez]

- Use ujson instead of simplejson. [Jose Diaz-Gonzalez]

- Ignore compiled python files. [Jose Diaz-Gonzalez]

- Fixed imports. [Jose Diaz-Gonzalez]

- Fixed up readme instructions. [Jose Diaz-Gonzalez]

- Refactor transports so that connections are no longer global. [Jose
  Diaz-Gonzalez]

- Readme and License. [Jose Diaz-Gonzalez]

- First commit. [Jose Diaz-Gonzalez]


