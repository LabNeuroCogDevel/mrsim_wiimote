#!/usr/bin/env python

from Pos import Pos
from xwii import connect_wii
import xwiimote
from Brain import glBrain
import InfoDialog


### connect to device

# will exit if 2 keys are pushed or wii disconnects (when count=2)
exit_count = 0

# connect to wii
try:
    (dev, p, evt) = connect_wii()
except Exception as e:
    InfoDialog.errorMsg("failed connect to wii: %s" % e)
    exit(1)

# how to track position
pos = Pos()
win = glBrain()

# who's position are we tracking
dlg = InfoDialog.InfoDialog()
sid, age = dlg.run()

total_rot = 0
while exit_count < 2:
    p.poll()
    try:
        dev.dispatch(evt)
        if evt.type == xwiimote.EVENT_KEY:
            code, state = evt.get_key()
            print("Key:", code, ", State:", state)
            exit_count += 1
        elif evt.type == xwiimote.EVENT_GONE:
            print("Gone")
            exit_count = 2
        elif evt.type == xwiimote.EVENT_MOTION_PLUS:
            # None when still collecint samples. number otherwise
            dist = pos.add_trans(evt.get_abs(0))
            if dist:
                print("dist: ", dist)
        elif evt.type == xwiimote.EVENT_ACCEL:
            # None when still collecint samples. number otherwise
            rot = pos.add_rot(evt.get_abs(0))
            if rot:
                total_rot = (total_rot + rot) % 360
                print("rot: ", rot)
                win.update_angle(total_rot)

        else:
            print("unkown specified event:", evt.type)
    except IOError as e:
        print("IOError: ", e)

exit(0)
