.. _introduction:

Introduction
============

Background
----------

Beaver provides an lightweight method for shipping local log files to Logstash. It does this using redis, zeromq, tcp, udp, rabbit or stdout as the transport. This means you'll need a redis, zeromq, tcp, udp, amqp or stdin input somewhere down the road to get the events.

Events are sent in logstash's ``json_event`` format. Options can also be set as environment variables.

.. _`mit`:

MIT License
-----------

A large number of open source projects you find today are `GPL Licensed`_.
While the GPL has its time and place, it should most certainly not be your
go-to license for your next open source project.

A project that is released as GPL cannot be used in any commercial product
without the product itself also being offered as open source.

The MIT, BSD, ISC, and Apache2 licenses are great alternatives to the GPL
that allow your open-source software to be used freely in proprietary,
closed-source software.

Beaver is released under terms of `MIT License`_.

.. _`GPL Licensed`: http://www.opensource.org/licenses/gpl-license.php
.. _`MIT License`: http://opensource.org/licenses/MIT


Beaver License
----------------

    .. include:: ../../LICENSE.txt
