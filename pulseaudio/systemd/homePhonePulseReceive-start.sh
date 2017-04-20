#!/bin/sh
[ -d $RUN_DIR ] || mkdir -p ${RUN_DIR}
cd ${RUN_DIR}
/usr/local/bin/homePhonePulseReceive
