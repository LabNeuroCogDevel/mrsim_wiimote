
from math import sqrt
from select import poll, POLLIN
import xwiimote

def connect_wii():
    """
    connect wiimote return device, poll, and event
    """
    # display a constant
    print("Connecting to ", xwiimote.NAME_CORE)

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
        raise Exception("No wiimote to read")

    # create a new iface
    try:
        dev = xwiimote.iface(firstwiimote)
        fd = dev.get_fd()
        dev.open(dev.available() | xwiimote.IFACE_WRITABLE)

    except IOError as e:
        print("Do you have system device permission?", e)
        raise e

    ### 

    # TODO: normalize
    # dev.set_mp_normalization(10, 20, 30, 40)
    # x, y, z, factor = dev.get_mp_normalization()
    # print("mp normalized", x, y, z, factor)

    # read some values
    p = poll()
    p.register(fd, POLLIN)
    evt = xwiimote.event()
    return (dev, p, evt)

