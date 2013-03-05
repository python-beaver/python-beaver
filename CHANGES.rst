Changelog
=========

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

- Rabbitmq_exchange_type option fixed in the README. [Xabier de Zuazo]

- Add test requirements to setup. [Paul Garner]

- Allow beaver to accept custom transport classes. [Paul Garner]

- Make beaver slightly more amenable to test mocking and sort of fix the
  broken zmq test. [Paul Garner]

22 (2013-01-15)
---------------

- Handle sigterm properly. Refs #87. [Jose Diaz-Gonzalez]

- Add --loglevel as alias for --output. Closes #92. [Jose Diaz-Gonzalez]

- Added logging on connection exception. [Thomas Morse]

- Add '--format raw' to pass through input unchanged. [Stephen Sugden]

- Fix string & null formatters in beaver.transport. [Stephen Sugden]

  the inline definitions were expecting a self parameter, which is *not*
  passed when you assign a function to an attribute on an object
  instance.

- Adding exception when redis connection can't be confirmed. [William
  Jimenez]

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

  Python's base glob.iglob does not operate as if globstar were in
  effect. To
  explain, let's say I have an erlang application with lager logs to
  
  /var/log/erl_app/lags.log
  /var/log/erl_app/console/YEAR_MONTH_DAY.log
  
  and webmachine logs to
  
  /var/log/erl_app/webmachine/access/YEAR_MONTH_DAY.log
  
  Prior to this commit, when configured with the path
  `/var/log/**/*.log` all
  webmachine logs would be ignored by beaver. This is no longer the
  case, to an
  arbitrary depth.
  
  Signed
  off
  by: Brian L. Troutwine <brian@troutwine.us>

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

- Fix missing underscore causing transport to break. [Norman Joyner]

- Implement redis auth support. [Norman Joyner]

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

- Reload tailed files on non-linux platforms. [Jose Diaz-Gonzalez]

  Python has an issue on OS X were the underlying C implementation of
  `file.read()` caches the EOF, therefore causing `readlines()` to only
  work once. This happens to also fail miserably when you are seeking to
  the end before calling readlines.
  
  This fix solves the issue by constantly re
  reading the files changed.
  
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
  potential for breakage, and socket.gethostname doesn't always return
  an
  FQDN, it's now an option to explicitly always use the fqdn.
  
  Fixes #68

- Check for log file truncation fixes #55. [Jeremy Kitchen]

  This adds a simple check for log file truncation and resets the watch
  when detected.
  
  There do exist 2 race conditions here:
  1. Any log data written prior to truncation which beaver has not yet
  read and processed is lost. Nothing we can do about that.
  2. Should the file be truncated, rewritten, and end up being larger
  than
  the original file during the sleep interval, beaver won't detect
  this. After some experimentation, this behavior also exists in GNU
  tail, so I'm going to call this a "don't do that then" bug :)
  
  Additionally, the files beaver will most likely be called upon to
  watch which may be truncated are generally going to be large enough
  and slow
  filling enough that this won't crop up in the wild.

- Add a version number to beaver. [Jose Diaz-Gonzalez]

10 (2012-12-15)
---------------

- Fixed package name. [Jose Diaz-Gonzalez]

- Regenerate CHANGES.rst on release. [Jose Diaz-Gonzalez]

- Adding support for /path/{foo,bar}.log. [Josh Braegger]

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

- Consistency. [Chris Faulkner]

- Stating the obvious. [Chris Faulkner]

- Grist for the mill. [Chris Faulkner]

- Drop redundant README.txt. [Chris Faulkner]

- Don't use empty string for tag when no tags configured in config file.
  [Stylianos Modes]

- Making 'mode' option work for zmqtransport.  Adding setuptools and
  tests (use ./setup.py nosetests).  Adding .gitignore. [Josh Braegger]

9 (2012-11-28)
--------------

- More release changes. [Jose Diaz-Gonzalez]

- Fixed deprecated warning when declaring exchange type. [Rafael
  Fonseca]

7 (2012-11-28)
--------------

- Added a helper script for creating releases. [Jose Diaz-Gonzalez]

- Partial fix for crashes caused by globbed files. [Jose Diaz-Gonzalez]

- Removed deprecated usage of e.message. [Rafael Fonseca]

- Fixed exception trapping code. [Rafael Fonseca]

- Added some resiliency code to rabbitmq transport. [Rafael Fonseca]

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

- Timestamp in ISO 8601 format with the "Z" sufix to express UTC.
  [Xabier de Zuazo]

- Adding udp support. [Morgan Delagrange]

- Lpush changed to rpush on redis transport. This is required to always
  read the events in the correct order on the logstash side. See: https:
  //github.com/logstash/logstash/blob/6f745110671b5d9d66bf082fbfed99d145
  af4620/lib/logstash/outputs/redis.rb#L4. [Xabier de Zuazo]

2 (2012-10-25)
--------------

- Example upstart script. [Michael D'Auria]

- Fixed a few more import statements. [Jose Diaz-Gonzalez]

- Fixed binary call. [Jose Diaz-Gonzalez]

- Refactored logging. [Jose Diaz-Gonzalez]

- Improve logging. [Michael D'Auria]

- Removed unnecessary print statements. [Jose Diaz-Gonzalez]

- Add default stream handler when transport is stdout. Closes #26. [bear
  (Mike Taylor)]

- Handle the case where the config file is not present. [Michael
  D'Auria]

- Better exception handling for unhandled exceptions. [Michael D'Auria]

- Fix wrong addfield values. [Alexander Fortin]

- Add add_field to config example. [Alexander Fortin]

- Add support for add_field into config file. [Alexander Fortin]

- Minor readme updates. [Jose Diaz-Gonzalez]

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

- When sending data over the wire, use UTC timestamps. [Darren Worrall]

- Support globs in file paths. [Darren Worrall]

- Added msgpack support. [Jose Diaz-Gonzalez]

- Use the python logging framework. [Jose Diaz-Gonzalez]

- Fixed Transport.format() method. [Jose Diaz-Gonzalez]

- Properly parse BEAVER_FILES env var. [Jose Diaz-Gonzalez]

- Refactor transports. [Jose Diaz-Gonzalez]

  Fix the json import to use the fastest json module available
  
  Move formatting into Transport class

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


