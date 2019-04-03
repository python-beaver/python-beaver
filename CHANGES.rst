Changelog
=========

36.3.1 (2019-04-03)
-------------------
------------------------
- Require pika version below 1.0.0. [Michael Contento]


36.3.0 (2018-10-14)
-------------------

Fix
~~~
- Correct release process. [Jose Diaz-Gonzalez]

Other
~~~~~
- Fix typo in RABBITMQ_ARGUMENT system property. [eroberts]
- Add arbitrary RabbitMQ arguments - Updated transport to parse
  arguments -Updated config.py to add system property - Updated user
  usage documentation - Confirmed no change in functionality if args are
  not passed. [eroberts]
- Usage fix. [Scott Brenner]

  Fixed missing/incorrect TCP option.
- Remove truncating of logline after 32766 chars (#422) [Robert
  Wunderer]

  * Remove truncating of logline after 32766 chars

  It is not necessary to limit unicode()'s input to 32766 chars, while
  doing puts an arbitrary limit on the length of lines beaver can
  handle.

  * Pin moto version to fix tests

  * multiline_regex_before won't work when logfile ends with empty line

  * Revert "multiline_regex_before won't work when logfile ends with empty line"

  This reverts commit 5196789916afa184beb71a0ef86344d7580d9136.

  * Fix README link

  * Remove truncating of logline after 32766 chars

  It is not necessary to limit unicode()'s input to 32766 chars, while
  doing puts an arbitrary limit on the length of lines beaver can
  handle.
- Fix README link. [Jamie Cressey]
- Revert "multiline_regex_before won't work when logfile ends with empty
  line" [Jamie Cressey]

  This reverts commit 5196789916afa184beb71a0ef86344d7580d9136.
- Multiline_regex_before won't work when logfile ends with empty line.
  [jeroenmaelbrancke]
- Pin moto version to fix tests. [Jamie Cressey]
- Fixing primary key reuse issues. [Javier Villar]
- Limiting number of records in batch to 500 as this is the kinesis
  limit. [Greg Sterin]
- Updating docs for number_of_consumer_processes config. [Greg Sterin]
- Avoid unreference variable 'st' error if file was removed. Raise
  exception if unrecognized environment error from os.stat. [Greg
  Sterin]
- Fix GitHub links. [Robin Baumgartner]

  The project was renamed to 'python-beaver', but the links do not reflect that change.


36.2.0 (2016-04-12)
-------------------
- Replaced Mosquitto with Paho-mqtt for mqtt transport. [Justin van
  Heerde]
- Add log file rotate in limit size. [soarpenguin]
- Fix README.rst docs link. [Andrew Grigorev]


36.0.1 (2016-01-13)
-------------------
- Fix README.rst formatting for rst-lint. [Jose Diaz-Gonzalez]
- Remove tabs and use "except .. as .." [EYJ]
- Try to fix hanging test by joining leftover thread. [EYJ]
- Fix Queue timeout occurring after successful reconnect. [EYJ]
- Fix rabbitmq reconnection behaviour to use the beaver reconnect
  mechanism. [EYJ]
- Migrating repo locations. [Jamie Cressey]
- Fixups for CONTRIBUTING. [Jamie Cressey]
- Fixing formatting. [Jamie Cressey]
- Changes to guidelines and adding reference to README. [Jamie Cressey]
- Adding contributing guidelines. [Jamie Cressey]


36.0.0 (2015-12-15)
-------------------
- Adding max_queue_size to docs. [Jamie Cressey]
- Pinning kafka-python version. [Jamie Cressey]
- Ensure we test against the latest version of kafka-python. [Jamie
  Cressey]
- Attempt to reconnect to Kafka on failure. [Jamie Cressey]
- Adding SQS tests. [Jamie Cressey]
- Exclude gh-pages from TravisCI runs. [Jamie Cressey]
- Adding coverage results to README. [Jamie Cressey]
- Adding coverage tests. [Jamie Cressey]
- We say Py2.6+ is a requirement, but do the tests actually pass on 2.6?
  [Jamie Cressey]
- Dont test py3, yet... [Jamie Cressey]
- Testing python 3.x. [Jamie Cressey]
- Using new travis config. [Jamie Cressey]
- Added requests as a dependency. [Jose Diaz-Gonzalez]

  Closes #304
- Bump debian version on release. [David Moravek]
- Support both older and newer pika. [Tim Stoop]
- Make reconnecting to a lost RabbitMQ work. [Tim Stoop]
- Remove old worker code in favor of the - now non-experimental -
  TailManager. [Jose Diaz-Gonzalez]


35.0.2 (2015-12-03)
-------------------
- Write to the SQS object not the dict when using sqs_bulk_lines flag.
  [Jamie Cressey]


35.0.1 (2015-11-26)
-------------------
- Remove autospec attribute. [Jose Diaz-Gonzalez]

  For some reason, this broke attribute setting on the mock SelectConnection.
- Fix pika version to version with all named parameters. [Jose Diaz-
  Gonzalez]
- Peg kafka to a known-good version. [Jose Diaz-Gonzalez]


35.0.0 (2015-11-26)
-------------------
- Remove gitchangelog.rc. [Jose Diaz-Gonzalez]
- Merging changes. [Jamie Cressey]
- Added configuration option ignore_old_files. [Ryan Steele]

  Files older then n days are ignored
- Support writes into multiple redis namespaces. [Andrei Vaduva]
- Adding support for multiple SQS queues. [Jamie Cressey]
- Ensure log lines confirm to utf-8 standard. [Jamie Cressey]

  We've come across cases when certain characters break Beaver transmitting log lines. This PR ensures all log lines correctly conform to UTF-8 when they're formatted for transmission.
- Set timeout to 1 second. [Tim Stoop]

  Apparantly, it needs to be an integer, so we cannot use pika's default
  of .25.
- Revert "Lower the default to .25, which is pika's default." [Tim
  Stoop]

  This reverts commit 17157990a272e458cc9253666f01c6002b84bda8.
- Lower the default to .25, which is pika's default. [Tim Stoop]

  As suggested by @kitchen.
- Pieter's patch for rabbitmq timeout. [Tim Stoop]
- Typo in config variable default value. [Jamie Cressey]
- Fix regressed change. [Jamie Cressey]
- Ability to send multiple log entries per single SQS message. [Jamie
  Cressey]
- Adding AWS profile authentication to SQS transport. [Jamie Cressey]


34.1.0 (2015-08-10)
-------------------
- Adding AWS SNS as a transport option. [Jamie Cressey]


34.0.1 (2015-08-07)
-------------------
- Revert some breakages caused by
  d159ec579c01b8fab532b3814c64b0ff8b2063ff. [Jose Diaz-Gonzalez]

  Closes #331
- Set default for command. [Jose Diaz-Gonzalez]
- #323 - fix tests to run with pika SelectConnection. [Tom Kregenbild]
- #323 - fix RabbitMQ transport _on_open_connection_error function to
  print connection errors. [Tom Kregenbild]
- #323 1. Add clear debug prints with queue size (one print every 1000
  items in order not to hurt performance) 2. If main queue is empty keep
  running and do nothing 3. In case of a timeout from main queue restart
  queue. [Tom Kregenbild]
- #323 - Change RabbitMQ pika to use Asynchronous SelectConnection
  instead of BlockingConnection for better performance. [Tom Kregenbild]
- #323 - add the ability to increase the number of Queue consumers by
  creating additional processes while running with --experimental flag.
  [Tom Kregenbild]
- #323 - add the ability to increase the number of Queue consumers by
  creating additional processes. [Tom Kregenbild]
- #323 - print current queue size and number of total number transports
  in debug mode in order to find problem in transport rate. [Tom
  Kregenbild]


34.0.0 (2015-07-24)
-------------------
- Added ssl-tcp key file support. [babbleshack]
- Rename configuration dir and debian bin to python-beaver. [David
  Moravek]
- Rename debian package back to python-beaver. [David Moravek]
- Debian packaging code review; thx @mnicky. [David Moravek]
- Improves debian packaging. [David Moravek]
- Fix tests when ZMQ is not installed. [David Moravek]
- Fix tests for python 2.7 (add funcsigs test dependency) [David
  Moravek]
- Move badge to below header. [Jose Diaz-Gonzalez]
- Add constants for data types, validate in init, use callback map.
  [Hector Castro]
- Move data type method conditional outside of loop. [Hector Castro]
- Add channel support to Redis transport. [Hector Castro]

  This changeset adds support for publishing log entries to a Redis
  channel, which is also supported by Logstash's Redis input.

  Beaver configuration files can now supply a `redis_data_type` key. Valid
  values for this key are `list` and `channel`. If left unset, the default
  is `list`.

  Attempts to resolve #266.
- Introduced a stomp transport for beaver using stomp.py. [Peter
  Lenderyou]
- Fix references to ConfigParser error classes. [Jose Diaz-Gonzalez]
- Redis transport: handle multiple connections and use them in round
  robin style. [musil]
- Fixes GELF format according to specs. [Marvin Frick]

  GELF formatted messages need to be \0 ended. At least for sending over
  TCP.
- Kafka round robin partitioner. [David Moravek]
- Solve error: cannot convert argument to integer. [Theofilis George-
  Nektarios]

  See at #312


33.3.0 (2015-04-08)
-------------------
- Basic docs for GELF formatter. [Oleg Rekutin]

  Also fixes formatting issues with the immediately-preceding HTTP
  transport example section.
- Adds a GELF formatter. [Oleg Rekutin]

  short_message is truncated to 250 characters and only the first line is
  retained. Pair with the HTTP POST output to write directly to graylog2.
- Issue #305, accept any 2xx code for http_transport. [Oleg Rekutin]


33.2.0 (2015-03-11)
-------------------
- Improved kafka test. [Marcel Casado]
- Added example of kafka transport usage in the user docs. [Marcel
  Casado]
- Added placeholder "dist" directory to download kafka binaries. [Marcel
  Casado]
- Added integration test support for Kafka transport. [Marcel Casado]
- Wrapped kafka client init in a try catch. [Marcel Casado]
- Initial kafka transport impl. [Marcel Casado]
- Updating config examples and docs. [Jonathan Sabo]
- Adding support for sqs queues in different accounts. [Jonathan Sabo]


33.1.0 (2015-02-04)
-------------------
- Improved error message for missing logstash_version. [Florian Hopf]

  Added a comment that the version needs to be set in the config
- Specify stricter dependency on python-daemon, fixes #286. [Graham
  Floyd]
- Add message_batch size checking since SQS can only handle 256KiB in a
  batch. Flush queue if message_batch is 10 messages or >= 250KiB.
  [Lance O'Connor]
- Explained valid values and meaning for rabbitmq_delivery_mode. [Fabio
  Coatti]
- Added documentation for rabbitmq_delivery_mode configuration
  parameter. [Fabio Coatti]
- A small change in except syntax. This should make happy python3 and
  work also in 2.6 and later. [Fabio Coatti]
- When sending a message, now we can tell rabbitmq which delivery mode
  we want, according to main configuration option
  rabbitmq_delivery_mode. [Fabio Coatti]
- Added configuration option for rabbitmq deliveryMode. Basically it
  works like a boolean, but having 1 and 2 as allowed values, we
  consider it integer and validate it as such. [Fabio Coatti]
- Newline removed. [Fabio Coatti]
- Added stanzas specific redis_namespace key to documentation. [Fabio
  Coatti]
- Added a space after comma, more compliant with python style guide.
  [Fabio Coatti]
- Revert "ignored eric files" [Fabio Coatti]

  This reverts commit ea2a6b27437570aeda3ee53b6c6ebd7ebb1f4f2a.

  as suggested, leave alone .gitignore :)
- This small commit allows to specify a redis namespace in file section
  of configuration file (stanzas). Basically, beaver checks if a
  redis_namespace is defined for the current file. If yes, it is used
  for the redis payload. If not (or null), beaver uses the
  redis_namespace value specified in global section. [Fabio Coatti]
- Added a section (stanza) configuration option in order to be able to
  specify a redis namespace. If set, it will override the namespace set
  in main section. Default is null. [Fabio Coatti]
- Ignored eric files. [Fabio Coatti]
- Remove `python-daemon` from requirements on win32. [Ryan Davis]

  If we're installing on windows, don't require `python-daemon`. This
  fixes a problem where trying to `pip install beaver` errors out when
  trying to install `python-daemon`.

  refs #141
- Use new repository name for travis-ci badge. [Jose Diaz-Gonzalez]


33.0.0 (2014-10-14)
-------------------
- Extend release script to support new, semver-tagged releases. [Jose
  Diaz-Gonzalez]
- Add gitchangelog.rc to fix changelog generation. [Jose Diaz-Gonzalez]


32 (2014-10-14)
---------------
- Allow for the config file to override the logfile's setting. [Aaron
  France]
- Force update of sincedb when beaver stop. [Pierre Fersing]
- Fixed sincedb_write_interval (Bugs #229). [Pierre Fersing]
- Fix config.get('ssh_options') [svengerlach]

  ssh_options could never be returned due to a wrong type check
- Add debian packaging based on dh-virtualenv. [Jose Diaz-Gonzalez]
- Zmq3 split HWM into SNDHWM/RCVHWM. Closes #246. [Pete Fritchman]
- Fix typo in usage.rst. [Hugo Lopes Tavares]

  s/logstash_verion/logstash_version/
- Fixed badge to point to master branch only. [Jose Diaz-Gonzalez]


31 (2014-01-25)
---------------

Fix
~~~
- Beaver user can't write its pid nor its log. [Mathieu Lecarme]

  Using a folder is the tactic used by Redis on Debian.

Other
~~~~~
- Add required spacing to readme for proper pypi doc support. [Jose
  Diaz-Gonzalez]
- Change release process to include processing of documentation. [Jose
  Diaz-Gonzalez]
- Use GlobSafeConfigParser to parse config files. [Clay Pence]

  In order to support all of the kinds of globs, pass GlobSafeConfigParser
  into the Configuration object so that it parses section headers
  correctly.

  Update dependency on conf_d

  Fix line spacing + trigger travis

  Remove chdir in test

  This should fix the unit test to run properly when run from the main
  directory.
- Fix redis_transport.py redis exception handling. Fixes #238. [Hugo
  Lopes Tavares]
- Attempt to fix memory leaks. Closes #186. [Jose Diaz-Gonzalez]
- Allow for newer versions of boto to be used. Closes #236. [Jose Diaz-
  Gonzalez]
- When shipping logs, use millisecond-precision timestamps. [Ryan Park]

  Logstash 1.3.2 has a problem with microsecond-precision timestamps in the
  @timestamp field, which is the default behavior of Python's .isoformat
  method. Logstash uses the JodaTime library to parse timestamps, and Joda
  doesn’t support nanosecond timestamp resolution. As a result, Logstash
  1.3.2 throws an exception on every log item shipped from Beaver.

  There's a discussion about this issue in the logstash-users mailing list,
  including an example of the Logstash exception:
      https://groups.google.com/forum/#!topic/logstash-users/wIzdv15Iefs

  This patch reduces @timestamp to millisecond precision, which should
  correct the problem with Beaver 1.3.2.
- Improve compatibility with case-sensitive filesystems. [Jose Diaz-
  Gonzalez]
- Modify test cases to support logstash_version. [Jose Diaz-Gonzalez]
- Document usage of logstash_version. [Peter Burkholder]
- Add add_field_env option to the config file to allow fields to be
  added using values from the environment. [Lance O'Connor]

  Closes #214
- Add SSL/TLS support to the RabbitMQ transport. Closes #217. [Jonathan
  Harker]
- Added http transport option. Closes #218. [Jeff Bryner]
- Adding missing config file option 'rabbitmq_queue_durable'. [Daniel
  Whelan]
- `StrictRedis.from_url` is better than DIY-ing it. [Kristian Glass]

  Note currently `fakeredis` doesn't support `from_url` - this is blocking
  on https://github.com/jamesls/fakeredis/pull/29 being merged in (I've
  bumped version requirement in `tests.txt` accordingly)
- Python 2.6 ConfigParser does not handle non-string Fixed typo.
  [tommyulfsparre]
- Dont add empty object to input list. [tommyulfsparre]
- Import threading library in tail manager since we want to use it.
  [Chris Roberts]
- Add SSL to the TCP Transport. [Simon McCartney]
- Redirect all docs to readthedocs. Refs #150. [Jose Diaz-Gonzalez]
- Readthedocs support. Closes #150. [Jose Diaz-Gonzalez]
- Convert producer to process. Allow timed producer culling. [Chris
  Roberts]
- Make consumer check threaded to prevent wedge state. [Chris Roberts]
- Don't crash on a string decoding exception. [Adam Twardowski]
- Set transport as valid on connect (properly resets for reconnect)
  [Chris Roberts]
- Handle publication failures in the TCP transport correctly. [Kiall Mac
  Innes]
- Add config option to manipulate ssh_options. [Andreas Lappe]

  This option allows to pass all ssh options to the tunnel.
- Fix version lookup. [Jose Diaz-Gonzalez]
- Moved multiline_merge function to utils.py. [Pierre Fersing]
- Support for multi-line and tail_lines options. [Pierre Fersing]
- Support for multi-line events in tail-version. [Pierre Fersing]
- Support for multi-line events. [Pierre Fersing]
- Ignore invalid rawjson log. [Tomoyuki Sakurai]

  this ensures beaver keeps running even when other application logged
  logs in invalid json format.
- Removed duplicate self._current_host from @source field. Fixes #180.
  [Alexander Papaspyrou]


30 (2013-08-22)
---------------
- Use os._exit over sys.exit in signal handlers to quit cleanly.
  [Kristian Glass]

  As per
  http://thushw.blogspot.co.uk/2010/12/python-dont-use-sysexit-inside-signal.html
  the use of `sys.exit` inside the signal handlers means that a
  `SystemExit` exception is raised
  (http://docs.python.org/2/library/sys.html#sys.exit) which can be caught
  by try/except blocks that might have been executing at time of signal
  handling, resulting in beaver failing to quit
- Allow string escapes in delimiter. [Michael Mittelstadt]

  As far as I can tell, there is no way for me to represent a newline as
  a delimiter in a configuration file with ConfigParser. I want to do this:

        [/ephemeral_storage/logs/kind_of_special.log]
        tags: special
        type: special
        delimiter: \n\n

  As the log has a blank line between its multiline entries.

  My change allows that, by making delimiter not string-escaped until
  after the config file is parsed. I'm naive about python, so there is a
  strong possibility I've gone about it horribly wrong. This would also
  easily allow splitting on nulls, tabs, unicode characters and other
  things that ConfigParser may not find kosher.

  By doing this sort of multiline parsing with beaver, it allows one to
  run logstash without the multiline filter, which due to its lack of
  thread-safety, forces you to run logstash with only one worker thread.
- CONFIG_DIR to CONFD_PATH. [iyingchi]
- Added doc for -C option for config directory. [iyingchi]
- Fixed example in Readme.rst for sqs_aws_secret_key. [Jonathan Quail]
- Allow path to be None. [Lars Hansson]

  Allow path to be set empty (None) in the configuration filer. This way
  all files and globs can be configured in files in confd_path.
- Fix zmq transport tests. [Scott Smith]
- Move zmq address config parsing into _main_parser. [Scott Smith]
- Allow specifying multiple zmq addresses to bind/connect. [Scott Smith]
- Redis 2.4.11 is no longer available on Pypi. [Andrew Gross]

  Fixes issue #167
- Add a TCP transport. [Kiall Mac Innes]
- Isolate connection logic. Provide proper reconnect support. [Chris
  Roberts]
- Corrected documentation for exclude tag. Closes #157. [Jose Diaz-
  Gonzalez]
- Add missing sqlite3 module to documentation. [Andreas Lappe]
- Tests status. [Denis Orlikhin]
- Travis integration. [Denis Orlikhin]
- Tests fix (conf_d does work without existing file) [Denis Orlikhin]
- Implicit broken zmq error handling. [Denis Orlikhin]


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

  Each worker has a `self._file_map` attribute which is a mapping of file ids to file data. When retrieving lines or checking on the status of the file, we use `iteritems()` which gives us a generator as opposed to a copy such as with `items()`. This generator allows us to iterate over the files without having issues where the file handle may open several times or other random Python issues.

  Using a generator also means that the set that we are iterating over should not change mid-iteration, which it does if a file is unwatched. To circumvent this, we should use a separate list to keep track of files we need to unwatch or rewatch, and do it out of band.

  We should also take care to catch `RuntimeError` which may arise when closing the Worker out of band - such as in the `cleanup` step of the worker dispatcher - but nowhere else.

  This should fix issues where logrotate suddenly causes files to disappear for a time and beaver tries to tail the file at the exact time it is being recreated.
- Typo in SQS docs. [Jonathan Quail]
- Remove ujson requirement. [Jose Diaz-Gonzalez]

  This allows users that do not have a compiler in their deployment area to install beaver.

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
- 'type' instead of 'exchange_type' in recent pika vers. [Pravir
  Chandra]
- Adding options to make queues durable and HA. [Pravir Chandra]
- Respect stat_interval file configuration in stable worker. [Jose Diaz-
  Gonzalez]
- Unified configuration file using conf_d module. [Jose Diaz-Gonzalez]

  This change adds support for a conf.d directory - configured only via the `--confd-path` flag - which allows beaver to read configuration from multiple files.

  Please note that the primary `beaver` stanza MUST be located in the file specified by the `--configfile` argument. Any other such `beaver` stanzas will be ignored.

  This change also unifies the `BeaverConfig` and `FileConfig` classes, and simplifies the api for retrieving global vs file-specific data.

  Please note that this commit BREAKS custom transport classes, as the interface for creating a transport class has changed. If you are referencing a `file_config.get(field, filename)` anywhere, please omit this and refer to `beaver_config.get_field(field, filename)`.

  Closes #107
- Hack to prevent stupid TypeError: 'NoneType' when running tests via
  setup.py. [Jose Diaz-Gonzalez]
- Properly handle rotated files on Darwin architectures. [Jose Diaz-
  Gonzalez]
- Log to debug instead of warning for file reloading on Darwin
  architectures. [Jose Diaz-Gonzalez]
- Speed up experimental worker. [Jose Diaz-Gonzalez]

  - Removed inline sleep call, which slowed down passes n*0.1 seconds, where n is the number of files being tailed
  - Inline methods that update data structures which should speed up larger installations
  - Make self.active() an attribute lookup instead of a method call
- Use latest version of message pack interface (0.3.0). Closes #128.
  [Jose Diaz-Gonzalez]
- Alternative for reading python requirements. [Justin Lambert]
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
- Auto-reconnect mechanism for the SSH tunnel. [Michael Franz Aigner]
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
- Fixing outdated transport docs. [Morgan Delagrange]


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


23 (2013-02-20)
---------------
- Worker: pretty format debug message "Iteration took %.6f" [Sergey
  Shepelev]
- Zeromq_hwm int() conversion moved to config. [Denis Orlikhin]
- Zeromq_hwm config entry. [Denis Orlikhin]
- Zeromq_hwm support. [Denis Orlikhin]
- Add test requirements to setup. [Paul Garner]
- Allow beaver to accept custom transport classes. [Paul Garner]
- Rabbitmq_exchange_type option fixed in the README. [Xabier de Zuazo]
- Make beaver slightly more amenable to test mocking and sort of fix the
  broken zmq test. [Paul Garner]


22 (2013-01-15)
---------------
- Handle sigterm properly. Refs #87. [Jose Diaz-Gonzalez]
- Add --loglevel as alias for --output. Closes #92. [Jose Diaz-Gonzalez]
- Added logging on connection exception. [Thomas Morse]
- Adding exception when redis connection can't be confirmed. [William
  Jimenez]
- Add '--format raw' to pass through input unchanged. [Stephen Sugden]
- Fix string & null formatters in beaver.transport. [Stephen Sugden]

  the inline definitions were expecting a self parameter, which is *not*
  passed when you assign a function to an attribute on an object instance.
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
- Implement fully recursive file globing. [Brian L. Troutwine]

  Python's base glob.iglob does not operate as if globstar were in effect. To
  explain, let's say I have an erlang application with lager logs to

      /var/log/erl_app/lags.log
      /var/log/erl_app/console/YEAR_MONTH_DAY.log

  and webmachine logs to

      /var/log/erl_app/webmachine/access/YEAR_MONTH_DAY.log

  Prior to this commit, when configured with the path `/var/log/**/*.log` all
  webmachine logs would be ignored by beaver. This is no longer the case, to an
  arbitrary depth.


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


17 (2012-12-28)
---------------
- Added missing python-daemon requirement. [Jose Diaz-Gonzalez]


16 (2012-12-27)
---------------
- Specify a max queue size of 100 to limit overrunning memory. [Jose
  Diaz-Gonzalez]
- Use multiprocessing for handling larger queue sizes. [Jose Diaz-
  Gonzalez]

  Previously there were issues where files that were updated frequently - such as varnish or server logs - would overwhelm the naive implementation of file.readlines() within Beaver. This would cause Beaver to slowly read larger and larger portions of a file before processing any of the lines, eventually causing Beaver to take forever to process log lines.

  This patch adds the ability to use an internal work queue for log lines. Whenever file.readlines() is called, the lines are placed in the queue, which is shared with a child process. The child process creates its own transport, allowing us to potentially create a Process Pool in the future to handle a larger queue size.

  Note that the limitation of file.readlines() reading in too many lines is still in existence, and may continue to cause issues for certain log files.
- Add default redis_password to BeaverConfig class. [Jose Diaz-Gonzalez]
- Fix missing underscore causing transport to break. [Norman Joyner]
- Implement redis auth support. [Norman Joyner]
- Add beaver init script for daemonization mode. [Jose Diaz-Gonzalez]
- Use python logger when using StdoutTransport. [Jose Diaz-Gonzalez]
- Add short arg flags for hostname and format. [Jose Diaz-Gonzalez]
- Add the ability to daemonize. Closes #79. [Jose Diaz-Gonzalez]
- Pass around a logger instance to all transports. [Jose Diaz-Gonzalez]
- Revert "Added a lightweight Event class" [Jose Diaz-Gonzalez]

  After deliberation, beaver is meant to be "light-weight". Lets leave
  the heavy-hitting to the big-boys.

  This reverts commit 1619d33ef4803c3fe910cf4ff197d0dd0039d2eb.
- Added a lightweight Event class. [Jose Diaz-Gonzalez]

  This class's sole responsibility will be the processing of a given line as an event.
  It's future goal will be to act as a lightweight implementation of the filter system within Logstash
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

  This argument was only used when no globs were specified in a config file.
  Since it is not configurable, there is no sense leaving around the extra logic.
- Remove extra callback invocation on readlines. [Jose Diaz-Gonzalez]
- Remove extra file_config module. [Jose Diaz-Gonzalez]
- General code reorganization. [Jose Diaz-Gonzalez]

  Move both BeaverConfig and FileConfig into a single class

  Consolidated run_worker code with code in beaver binary file. This will create a clearer path for Exception handling, as it is now the responsibility of the calling class, allowing us to remove duplicative exception handling code.

  Added docstrings to many fuctions and methods

  Moved extra configuration and setup code to beaver.utils module. In many cases, code was added hastily before.

  Made many logger calls debug as opposed to info. The info level should be generally reserved for instances where files are watched, unwatched, or some change in the file state has occurred.
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

  Useful for cases where we do not want any extra overhead on message formatting
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

  This code should allow us to create an ssh tunnel between two distinct servers for the purposes of sending and receiving data.

  This is useful in certain cases where you would otherwise need to whitelist in your Firewall or iptables setup, such as when running in two different regions on AWS.
- Allow for initial connection lag. Helpful when waiting for an SSH
  proxy to connect. [Jose Diaz-Gonzalez]
- Fix issue where certain config defaults were of an improper value.
  [Jose Diaz-Gonzalez]
- Allow specifying host via flag. Closes #70. [Jose Diaz-Gonzalez]


12 (2012-12-17)
---------------
- Reload tailed files on non-linux platforms. [Jose Diaz-Gonzalez]

  Python has an issue on OS X were the underlying C implementation of
  `file.read()` caches the EOF, therefore causing `readlines()` to only
  work once. This happens to also fail miserably when you are seeking to
  the end before calling readlines.

  This fix solves the issue by constantly re-reading the files changed.

  Note that this also causes debug mode to be very noisy on OS X. We all
  have to make sacrifices...
- Deprecate all environment variables. [Jose Diaz-Gonzalez]

  This shifts configuration management into the BeaverConfig class.
  Note that we currently throw a warning if you are using environment
  variables.

  Refs #72
  Closes #60
- Warn when using deprecated ENV variables for configuration. Refs #72.
  [Jose Diaz-Gonzalez]
- Minor changes for PEP8 conformance. [Jose Diaz-Gonzalez]


11 (2012-12-16)
---------------
- Add optional support for socket.getfqdn. [Jeremy Kitchen]

  For my setup I need to have the fqdn used at all times since my
  hostnames are the same but the environment (among other things) is
  found in the rest of the FQDN.

  Since just changing socket.gethostname to socket.getfqdn has lots of
  potential for breakage, and socket.gethostname doesn't always return an
  FQDN, it's now an option to explicitly always use the fqdn.

  Fixes #68
- Check for log file truncation fixes #55. [Jeremy Kitchen]

  This adds a simple check for log file truncation and resets the watch
  when detected.

  There do exist 2 race conditions here:
  1. Any log data written prior to truncation which beaver has not yet
     read and processed is lost. Nothing we can do about that.
  2. Should the file be truncated, rewritten, and end up being larger than
     the original file during the sleep interval, beaver won't detect
     this. After some experimentation, this behavior also exists in GNU
     tail, so I'm going to call this a "don't do that then" bug :)

     Additionally, the files beaver will most likely be called upon to
     watch which may be truncated are generally going to be large enough
     and slow-filling enough that this won't crop up in the wild.
- Add a version number to beaver. [Jose Diaz-Gonzalez]


10 (2012-12-15)
---------------
- Fixed package name. [Jose Diaz-Gonzalez]
- Regenerate CHANGES.rst on release. [Jose Diaz-Gonzalez]
- Adding support for /path/{foo,bar}.log. [Josh Braegger]
- Consistency. [Chris Faulkner]
- Stating the obvious. [Chris Faulkner]
- Grist for the mill. [Chris Faulkner]
- Drop redundant README.txt. [Chris Faulkner]
- Ignore file errors in unwatch method -- the file might not exists.
  [Josh Braegger]
- Unwatch file when encountering a stale NFS handle. When an NFS file
  handle becomes stale (ie, file was removed), it was crashing beaver.
  Need to just unwatch file. [Josh Braegger]
- Consistency. [Chris Faulkner]
- Pull install requirements from requirements/base.txt so they don't get
  out of sync. [Chris Faulkner]
- Include changelog in setup. [Chris Faulkner]
- Convert changelog to RST. [Chris Faulkner]
- Actually show the license. [Chris Faulkner]
- Consistent casing. [Chris Faulkner]
- Don't use empty string for tag when no tags configured in config file.
  [Stylianos Modes]
- Making 'mode' option work for zmqtransport.  Adding setuptools and
  tests (use ./setup.py nosetests).  Adding .gitignore. [Josh Braegger]


9 (2012-11-28)
--------------
- More release changes. [Jose Diaz-Gonzalez]
- Fixed deprecated warning when declaring exchange type. [Rafael
  Fonseca]


8 (2012-11-28)
--------------
- Removed deprecated usage of e.message. [Rafael Fonseca]
- Fixed exception trapping code. [Rafael Fonseca]
- Added some resiliency code to rabbitmq transport. [Rafael Fonseca]


7 (2012-11-28)
--------------
- Added a helper script for creating releases. [Jose Diaz-Gonzalez]
- Partial fix for crashes caused by globbed files. [Jose Diaz-Gonzalez]


6 (2012-12-15)
--------------
- Fix issue where polling for files was done incorrectly. [Jose Diaz-
  Gonzalez]
- Added ubuntu init.d example config. [Jose Diaz-Gonzalez]


5 (2012-12-15)
--------------
- Try to poll for files on startup instead of throwing exceptions.
  Closes #45. [Jose Diaz-Gonzalez]
- Added python 2.6 to classifiers. [Jose Diaz-Gonzalez]


4 (2012-12-15)
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
- Timestamp in ISO 8601 format with the "Z" sufix to express UTC.
  [Xabier de Zuazo]
- Adding udp support. [Morgan Delagrange]
- Lpush changed to rpush on redis transport. This is required to always
  read the events in the correct order on the logstash side. See: https:
  //github.com/logstash/logstash/blob/6f745110671b5d9d66bf082fbfed99d145
  af4620/lib/logstash/outputs/redis.rb#L4. [Xabier de Zuazo]


2 (2012-11-25)
--------------
- Example upstart script. [Michael D'Auria]
- Fixed a few more import statements. [Jose Diaz-Gonzalez]
- Fixed binary call. [Jose Diaz-Gonzalez]
- Refactored logging. [Jose Diaz-Gonzalez]
- Improve logging. [Michael D'Auria]
- Removed unnecessary print statements. [Jose Diaz-Gonzalez]
- Add default stream handler when transport is stdout. Closes #26. [bear
  (Mike Taylor)]
- Better exception handling for unhandled exceptions. [Michael D'Auria]
- Handle the case where the config file is not present. [Michael
  D'Auria]
- Fix wrong addfield values. [Alexander Fortin]
- Add add_field to config example. [Alexander Fortin]
- Add support for add_field into config file. [Alexander Fortin]
- Minor readme updates. [Jose Diaz-Gonzalez]
- Add support for type reading from INI config file. [Alexander Fortin]

  Add support for symlinks in config file

  Add support for file globbing in config file

  Add support for tags

  - a little bit of refactoring, move type and tags check down into
    transport class
  - create config object (reading /dev/null) even if no config file
    has been given via cli

  Add documentation for INI file to readme

  Remove unused json library

  Conflicts:
  	README.rst
- Support globs in file paths. [Darren Worrall]
- When sending data over the wire, use UTC timestamps. [Darren Worrall]
- Added msgpack support. [Jose Diaz-Gonzalez]
- Use the python logging framework. [Jose Diaz-Gonzalez]
- Fixed Transport.format() method. [Jose Diaz-Gonzalez]
- Properly parse BEAVER_FILES env var. [Jose Diaz-Gonzalez]
- Refactor transports. [Jose Diaz-Gonzalez]

  - Fix the json import to use the fastest json module available
  - Move formatting into Transport class
- Attempt to fix defaults from env variables. [Jose Diaz-Gonzalez]
- Fix README and beaver CLI help to reference correct RABBITMQ_HOST
  environment variable. [jdutton]
- Add RabbitMQ support. [Alexander Fortin]
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


1 (2012-11-25)
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


