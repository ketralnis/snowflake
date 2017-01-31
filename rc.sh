#!/bin/sh
#
# PROVIDE: snowflake
# REQUIRE: DAEMON networking
#
# Add the following lines to /etc/rc.conf to enable snowflake:
#
# snowflake_enable="YES"
#

. /etc/rc.subr

name=snowflake
rcvar=snowflake_enable
pidfile=/var/run/${name}.pid

start_cmd="${name}_start"
stop_cmd="${name}_stop"

load_rc_config $name

: ${snowflake_enable:=no}
: ${snowflake_flags=""}
: ${snowflake_db="/var/db/snowflake.db"}
: ${snowflake_user="root"}

snowflake_start() {
    /usr/sbin/daemon -c -f -u "$snowflake_user" -p "$pidfile" \
        /usr/local/bin/python2.7 -m snowflake.cmd \
        -d "$snowflake_db" --server $snowflake_flags
}

snowflake_stop() {
    kill `cat $pidfile`
    rm -f $pidfile
}

run_rc_command "$1"