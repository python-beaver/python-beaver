Experimental ports for beaver
=============================

This directory contains FreeBSD ports for beaver and its dependencies. Please
use at your own risk. Please report bug to MAINTAINER in Makefile or create
pull request at https://github.com/reallyenglish/beaver

Usage
-----

1. read [FreeBSD Porter's Handbook](http://www.freebsd.org/doc/en/books/porters-handbook/)
2. copy all subdirectories to your ${PORTSDIR}
3. add "beaver" entry to ${PORTSDIR}/UIDs and ${PORTSDIR}/GIDs. see an example
   at [reallyenglish/freebsd-ports@8a0d82a](https://github.com/reallyenglish/freebsd-ports/commit/8a0d82a29efd7d60ff81f1d981d10688273f762f)
4. run "cd sysutils/py-Beaver && make && make install" as root
5. edit /etc/rc.conf if necessary. see /usr/local/etc/rc.d/beaver for details.
6. create /usr/local/etc/beaver.conf
7. run "/usr/local/etc/rc.d/beaver start" as root

