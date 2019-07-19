#!/usr/bin/env python

# test with
# sudo LD_LIBRARY_PATH=<prefix>/lib PYTHONPATH=<prefix>/lib/python2.7/site-packages python ./swig/python/xwiimote_test.py

import errno
from time import sleep
from select import poll, POLLIN
from inspect import getmembers
from pprint import pprint
from math import sqrt
from time import sleep
import xwiimote
from Pos import Pos

# display a constant
print("Connecting to ", xwiimote.NAME_CORE)

### connect to device
# list wiimotes and remember the first one
try:
    mon = xwiimote.monitor(True, True)
    print("mon fd", mon.get_fd(False))
    ent = mon.poll()
    firstwiimote = ent
    while ent is not None:
        print("Found device: " + ent)
        ent = mon.poll()
except SystemError as e:
    print("ooops, cannot create monitor (", e, ")")

# continue only if there is a wiimote
if firstwiimote is None:
    print("No wiimote to read")
    exit(0)

# create a new iface
try:
    dev = xwiimote.iface(firstwiimote)
    fd = dev.get_fd()
    dev.open(dev.available() | xwiimote.IFACE_WRITABLE)

except IOError as e:
    print("Do you have system device permission?", e)
    exit(1)

### 

# TODO: normalize
# dev.set_mp_normalization(10, 20, 30, 40)
# x, y, z, factor = dev.get_mp_normalization()
# print("mp normalized", x, y, z, factor)

# read some values
p = poll()
p.register(fd, POLLIN)
evt = xwiimote.event()

# will exit if 2 keys are pushed or wii disconnects (n=2)
n = 0

pos = Pos()

while n < 2:
    p.poll()
    try:
        dev.dispatch(evt)
        if evt.type == xwiimote.EVENT_KEY:
            code, state = evt.get_key()
            print("Key:", code, ", State:", state)
            n+=1
        elif evt.type == xwiimote.EVENT_GONE:
            print("Gone")
            n = 2
        elif evt.type == xwiimote.EVENT_MOTION_PLUS:
            dist = pos.add_trans(evt.get_abs(0))
            if dist:
                print("dist: ", dist)
        elif evt.type == xwiimote.EVENT_ACCEL:
            rot = pos.add_rot(evt.get_abs(0))
            if rot:
                print("rot: ", rot)

        else:
            print("unkown specified event:", evt.type)
    except IOError as e:
        print("IOError: ", e)

exit(0)
