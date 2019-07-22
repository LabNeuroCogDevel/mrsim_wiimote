import pywavefront
from pywavefront import visualization
import pyglet
import ctypes
import time
from pyglet.gl import (
        glLoadIdentity, glTranslated, glRotatef,
        glLightfv, glEnable, glMatrixMode, gluPerspective,
        GL_LIGHTING, GL_LIGHT0, GL_POSITION, GL_PROJECTION, GL_MODELVIEW)


class glBrain(pyglet.window.Window):
    def __init__(self):
        super(glBrain, self).__init__()
        self.brain = pywavefront.Wavefront('uv_sphere.obj')
        # pywavefront.Wavefront('pial_Full_obj/lh.pial.obj')
        
        self.lightfv = ctypes.c_float * 4
        self.rotation = 0
        self.label = pyglet.text.Label('world',
                                       font_size=36,
                                       x=self.width//2,
                                       y=self.height//2)

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

        glTranslated(0.0, 0.0, -3.0)
        glRotatef(self.rotation, 0.0, 1.0, 0.0)
        glRotatef(-25.0, 1.0, 0.0, 0.0)
        glRotatef(45.0, 0.0, 0.0, 1.0)

        glEnable(GL_LIGHTING)

        visualization.draw(self.brain)
        print("draw @", self.rotation)

    def update(self, dt):
        self.rotation += 90.0 * dt
        self.rotation = self.rotation % 360

    def update_angle(self, angle):
        self.rotation = angle
        self.switch_to()
        self.dispatch_events()
        self.on_draw()
        self.flip()


if __name__ == "__main__":
    win = glBrain()
    # pyglet.clock.schedule(win.update)
    # pyglet.app.run()

    win.update_angle(0)
    time.sleep(.5)
    win.update_angle(90)
    time.sleep(.5)
    win.update_angle(270)
    time.sleep(.5)
