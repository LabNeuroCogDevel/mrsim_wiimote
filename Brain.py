import pywavefront
from pywavefront import visualization
import pyglet
import ctypes
import time
from pyglet.gl import (
        glLoadIdentity, glTranslated, glRotatef,
        glLightfv, glEnable, glMatrixMode, gluPerspective,
        GL_LIGHTING, GL_LIGHT0, GL_POSITION, GL_PROJECTION, GL_MODELVIEW)

"""
based heavily on pywavefrom example
"""

class glBrain(pyglet.window.Window):
    def __init__(self, pos=None, *kargs):
        super(glBrain, self).__init__(*kargs)
        self.set_fullscreen(True)
        self.brain = pywavefront.Wavefront('uv_sphere.obj')
        self.pos = pos
        # brain doesn't load as well as hoped
        # pywavefront.Wavefront('pial_Full_obj/lh.pial.obj')

        self.bg_color = (150,150,150,255)
        self.bg = pyglet.image.SolidColorImagePattern(self.bg_color).create_image(100,100)
        
        self.lightfv = ctypes.c_float * 4
        self.rots = [0]*3
        self.trans = [0]*3

    def on_resize(self, width, height):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60., float(width)/height, 1., 100.)
        glMatrixMode(GL_MODELVIEW)

        return True

    def on_draw(self):
        self.clear()

        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, self.lightfv(-1.0, 1.0, 1.0, 0.0))
        glEnable(GL_LIGHT0)

        self.trans[2] = -3 # center is z -3, dont move in z
        glTranslated(*self.trans)
        glRotatef(self.rots[0], 1.0, 0.0, 0.0)
        glRotatef(self.rots[1], 0.0, 1.0, 0.0)
        glRotatef(self.rots[2], 0.0, 0.0, 1.0)
        glRotatef(-25.0, 1.0, 0.0, 0.0)
        glRotatef(45.0, 0.0, 0.0, 1.0)

        glEnable(GL_LIGHTING)

        # cannot figure out how to make this always flat
        #self.bg.blit(0,0) 
        visualization.draw(self.brain)

        print("draw @", self.trans, self.rots)

    def on_key_press(self, sym, mod):
        """ leaky abstraction, need ref to pos to reset relative values
           L,S - start log
           R   - reset
           F   - undo fullscreen (broke)
           Q   - quit
        """
        if sym in [pyglet.window.key.L, pyglet.window.key.S]:
            pos.start_log()
        elif sym == pyglet.window.key.R:
            print('reset')
            if self.pos is not None:
                self.pos.reset()
        elif sym == pyglet.window.key.F:
            self.set_fullscreen(False)
            self.set_size(640,400)
        elif sym == pyglet.window.key.Q:
            exit(0)

    def alert(self, color=(0,0,0,255)):
        self.bg_color = color
        self.bg = pyglet.image.SolidColorImagePattern(self.bg_color).create_image(100,100)

    def update_pos(self, trans):
        self.trans = trans
        self.update()

    def update_angle(self, rots):
        self.rots = rots
        self.update()

    def update(self):
        self.switch_to()
        self.dispatch_events()
        self.on_draw()
        self.flip()


if __name__ == "__main__":
    win = glBrain(None, 1024,768)

    win.update_angle([0, 0, 0])
    time.sleep(.5)
    win.update_angle([90, 0, 0])
    time.sleep(.5)
    win.update_angle([0, 270, 0])
    time.sleep(.5)
    win.update_angle([0, -180, 0])
    time.sleep(.5)
    win.update_angle([0, 0, -270])
    time.sleep(.5)
