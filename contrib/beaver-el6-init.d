#!/bin/bash
#
# beaver      Startup script for beaver.
#
# chkconfig: 2345 13 87
# description: beaver is the facility by which logs are delivered to logstash
### BEGIN INIT INFO
# Provides: $beaver
# Required-Start: $syslog
# Required-Stop: $local_fs
# Default-Start:  2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: Logstash shipper
# Description: Beaver is a small python utility for shipping logs to logstash
### END INIT INFO

# Source function library.
. /etc/init.d/functions

RETVAL=0
PIDFILE=/var/run/beaver.pid

prog=beaver
exec=/usr/bin/beaver
lockfile=/var/lock/subsys/$prog

# Source config
if [ -f /etc/sysconfig/$prog ] ; then
    . /etc/sysconfig/$prog
fi

BEAVER_CONFIG=${BEAVER_CONFIG:-/etc/beaver.conf}

start() {
    [ -x $exec ] || exit 5
    [ -f $BEAVER_CONFIG ] || exit 7

    umask 077

    echo -n $"Starting beaver: "
    daemon $exec -D -P $PIDFILE -c $BEAVER_CONFIG $BEAVER_OPTIONS
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && touch $lockfile
    return $RETVAL
}
stop() {
    echo -n $"Shutting down beaver: "
    killproc -p "$PIDFILE" $exec
    RETVAL=$?
    echo
    [ $RETVAL -eq 0 ] && rm -f $lockfile
    return $RETVAL
}
rhstatus() {
    status -p "$PIDFILE" -l $prog $exec
}
restart() {
    stop
    start
}
case "$1" in
  start)
        start
        ;;
  stop)
        stop
        ;;
  restart)
        restart
        ;;
  reload)
        exit 3
        ;;
  force-reload)
        restart
        ;;
  status)
        rhstatus
        ;;
  condrestart|try-restart)
        rhstatus >/dev/null 2>&1 || exit 0
        restart
        ;;
  *)
        echo $"Usage: $0 {start|stop|restart|condrestart|try-restart|reload|force-reload|status}"
        exit 3
esac

exit $?
