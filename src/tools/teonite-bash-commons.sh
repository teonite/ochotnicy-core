#
# Copyright 2011-2014 (C) TEONITE - http://teonite.com
#
# Author: Robert Olejnik <robert@teonite.com>
#
# Description:
#
#  TEONITE Bourne Shell Common Library
#

# default variables {{{
ABSOLUTE_PATH=$(cd `dirname "${BASH_SOURCE[0]}"` && pwd)
ROOT_DIR=`dirname "${ABSOLUTE_PATH}"`

CURRENTDATE=`date +%Y%m%d`
[ "X$CFG_LOG_FILE" == "X" ] && CFG_LOG_FILE="${ROOT_DIR}/logs/${TNTCMNS_$$}.log"
TNT_SUPPORT="support@teonite.com"
# }}}

# FUNCTION DEFINITION {{{

# logging functions
# $1 - message
# $2 - log level
function logmsg
{
	typeset OPTIONS

	[ $LOG_PRIO ] && $OPTIONS="-p $LOG_PRIO"

	logger $OPTIONS "$*"

	msg=`echo "[$2] $1" | awk '{"date" | getline today;print today " " $0}'`

	[ $CFG_VERBOSE == 1 -o $CFG_DEBUG == 1 ] && echo $msg
	echo "$msg" >> $CFG_LOG_FILE

}

# log level = DEBUG 
function logdebug
{
	if [ $CFG_DEBUG != 0 ]; then
		logmsg "$1" "DEBUG"
	fi
} 

# log level = INFO
function loginfo
{
	logmsg "$1" "INFO"
}

# log level = ERROR
function logerror
{
	logmsg "$1" "ERROR"
}

# get header message
function print_header
{
	if [ "X${BASENAME}" == "X" ]; then
		BASENAME="OMNIu$$"
	fi

	if [ "X${CFG_VERSION}" == "X" ]; then
		BASENAME="v0.0.0"
	fi

	echo "$BASENAME v$CFG_VERSION, Copyright 2011-2014 (C) TEONITE"
	echo
}

log_then_run() {
	typeset OPTIONS

	[ $LOG_PRIO ] && $OPTIONS="-p $LOG_PRIO"

	logger $OPTIONS "$*"

	logdebug "Executing: $* 2>&1 >> ${CFG_LOG_FILE}"
	ERROR_MSG=$(eval $* 2>&1 >> ${CFG_LOG_FILE})
	ERROR_COD=$?

	if [ ${ERROR_COD} -ne 0 ]; then
		logerror "Execution of: $* failed:"
		logerror "${ERROR_MSG}"
		return ${ERROR_COD}
	fi
	return
}

error_msg()
{
    logerror "Unfortunately an error occurred."
    logerror "You can find more details in the following log file: ${CFG_LOG_FILE}"
    logerror "If you wish, you can contact TEONITE support line:"
    logerror "  + or by sending an email to: ${TNT_SUPPORT}"
    logerror "When contacting, please attach the following log file: ${CFG_LOG_FILE}"
}

# execute a command
run_cmd()
{
	MESSAGE=$1
	shift
	loginfo "${MESSAGE}"
	log_then_run "$*"
	return $?
}

# check if file exists
function check_file()
{
	if [ ! -f $1 ] ; then
		logerror "file $1 not found.. exiting" 1>&2
		return 0
	fi
}

# this function trims lines with "#" char
function show_config()
{
	cat $1 | sed "/^ *#.*/D" | sed "/^ *$/D"
}

# show configuration value
function show_field()
{
	echo $1 | cut -d':' -f$2
}
# end: function definition }}}

# }}}
