#!/bin/bash
#
# Small script to start the wii motion detection
# program. Checks to make sure it is not already
# running before starting. Niles Oien January 2013.
#

isRunning=`ps aux | grep wiiAngle.py | grep -v grep | wc -l`

cd $HOME/wii

if [ $isRunning -eq 0 ]; then
 xterm -fg green -fn 10x20 -bg black -title "wiiMotion data acquisition" -geometry 120x14+50+500 \
  -e ./wiiAngle.py &
else
 xterm -fg red -bg black -title Warning -geometry 48x2 \
 -e "echo WII SYSTEM IS ALREADY RUNNING, NOT STARTED; sleep 5" &> /dev/null &
fi


