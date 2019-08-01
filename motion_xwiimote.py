#!/usr/bin/env python

import sys
import xwiimote
from Brain import glBrain
import InfoDialog
from Pos import Pos
from xwii import connect_wii, rumble


### connect to device

# will exit if 2 keys are pushed or wii disconnects (when count=2)
exit_count = 0

# max dot product angle before rumbling
angleTol = 10.0
# count the number of times we go over angleTol and vibrate the wiimote
nrumble = 0

# connect to wii
try:
    (dev, p, evt) = connect_wii()
except Exception as e:
    InfoDialog.errorMsg("failed connect to wii: %s" % e)
    exit(1)

# who's position are we tracking
if len(sys.argv) != 3:
    dlg = InfoDialog.InfoDialog()
    sid, age = dlg.run()
else:
    sid, age = sys.argv[1:3]


# how to track position
pos = Pos(max_dot=angleTol)
# show a refernce for how much they're moving
# keys pushed in opengl can be passed on to functions in pos
win = glBrain(pos, 1024, 768)

# TODO: rumble does not work after glBrain is called
# win = None
# rumble(dev)

while exit_count < 2:
    p.poll()
    try:
        dev.dispatch(evt)
        # push 2 to recenter. and 1 (twice) to exit
        if evt.type == xwiimote.EVENT_KEY:
            code, state = evt.get_key()
            print("Key:", code, ", State:", state)
            if code == 10: # button 2, button 1 == 9
                # reset trans and rot
                pos.reset()
            else:
                exit_count += 1
        elif evt.type == xwiimote.EVENT_GONE:
            print("Gone")
            exit_count = 2
        elif evt.type == xwiimote.EVENT_MOTION_PLUS:
            # None when still collecint samples. number otherwise
            dist = pos.add_trans(evt.get_abs(0))
            if dist:
                print("e dist: ", dist)
                if win:
                    trans = [x/5000 for x in pos.rel_trans]
                    win.update_pos(trans)
        elif evt.type == xwiimote.EVENT_ACCEL:
            # None when still collecint samples. number otherwise
            rot = pos.add_rot(evt.get_abs(0))
            if rot:
                print("dot: ", rot)
                # rumble?
                if(rot > angleTol):
                    print("RUMBLE")
                    rumble(dev)
                # update display?
                if win: 
                    win.update_angle(pos.rel_rot)

        elif evt.type == xwiimote.EVENT_IR:
            continue
        else:
            print("unkown wiimote event:", evt.type)
    except IOError as e:
        print("IOError: ", e)

exit(0)
