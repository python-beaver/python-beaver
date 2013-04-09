#!/bin/bash -e
### BEGIN INIT INFO
# Provides:          beaver
# Required-Start:    $local_fs $remote_fs $network
# Required-Stop:     $local_fs $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start up the Beaver at boot time
# Description:       Enable Log Sender provided by beaver.
### END INIT INFO


# Documentation available at
# http://refspecs.linuxfoundation.org/LSB_3.1.0/LSB-Core-generic/LSB-Core-generic/iniscrptfunc.html
# Debian provides some extra function though
source /lib/lsb/init-functions


DAEMON_NAME="beaver"
DAEMON_USER="beaver"
DAEMON_PATH="$(which beaver)"
DAEMON_OPTS="-c /etc/beaver.conf"
DAEMON_PWD="${PWD}"

STARTUP_MSG="Starting log sender server daemon"
SHUTDOWN_MSG="Stopping log sender server daemon"

DAEMON_PID="/var/run/${DAEMON_NAME}.pid"
DAEMON_LOG="/var/log/${DAEMON_NAME}.log"
DAEMON_NICE=0

[ -r "/etc/default/${DAEMON_NAME}" ] && source "/etc/default/${DAEMON_NAME}"


do_start() {
	local result
	log_daemon_msg "${STARTUP_MSG}" "${DAEMON_NAME}"
	if [ -z "${DAEMON_USER}" ]; then
		start_daemon -n $DAEMON_NICE -p "${DAEMON_PID}" "${DAEMON_PATH}" $DAEMON_OPTS
		result=$?
		log_end_msg $result
	else
		start-stop-daemon --start --quiet --oknodo --background \
			--nicelevel $DAEMON_NICE \
			--chdir "${DAEMON_PWD}" \
			--pidfile "${DAEMON_PID}" --make-pidfile \
			--exec "${DAEMON_PATH}" -- $DAEMON_OPTS
		result=$?
		log_end_msg $result
	fi
	return $result
}

do_stop() {
	local result
	log_daemon_msg "${SHUTDOWN_MSG}" "${DAEMON_NAME}"
	killproc -p "${DAEMON_PID}" "${DAEMON_PATH}"
	result=$?
	log_end_msg $result
	return $result
}

do_restart() {
	local result
	do_stop
	result=$?
	if [ $result = 0]; then
		do_start
		result=$?
	fi
	return $result
}

do_status() {
	local result
	status_of_proc -p "${DAEMON_PID}" "${DAEMON_PATH}" "${DAEMON_NAME}"
	result=$?
	return $result
}

do_usage() {
	echo $"Usage: $0 {start | stop | restart | status}"
	exit 1
}

case "$1" in
start)   do_start;   exit $? ;;
stop)    do_stop;    exit $? ;;
restart) do_restart; exit $? ;;
status)  do_status;  exit $? ;;
*)       do_usage;   exit  1 ;;
esac
