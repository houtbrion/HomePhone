#!/bin/sh
[ -f ${PID_FILE} ] && kill -9 $(cat ${PID_FILE})
[ -f ${LOCK_FILE} ] && rm ${LOCK_FILE}
[ -f ${PID_FILE} ] && rm ${PID_FILE}
