from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import (AmbientLight, PointLight, Spotlight, 
                          AntialiasAttrib, KeyboardButton, TransparencyAttrib)
from math import sqrt
from toon.input.lsl_wrapper import LslDevice
from toon.input.hand import Hand
import numpy as np

class BlamDemo(ShowBase):
    
    def __init__(self, dev):
        ShowBase.__init__(self)
        
        render.setAntialias(AntialiasAttrib.MMultisample)
        render.setShaderAuto() # gets us shadows

        self.dev = dev
        self.zeroing = None
        self.load_models()
        self.setup_lights()
        self.setup_camera()
        taskMgr.add(self.move_task, 'move')
        taskMgr.add(self.colour_change, 'col')

    def load_models(self):
        self.background_model = loader.loadModel('background') # background.egg
        self.cube = loader.loadModel('cube')
        self.target = loader.loadModel('target')
        
        self.background_model.reparentTo(render)
        self.background_model.setScale(0.5, 0.5, 0.5) #TODO: Just make the original 1,1,1
        self.background_model.setPos(0, 0, -1) # Make the intersection 0, 0, 0
        
        # cube is a sanity check -- replace w/ proper obj
        self.cube.reparentTo(render)
        self.cube.setPos(-0.1, 0.2, 0.4)
        self.cube.setScale(0.05, 0.05, 0.05)

        self.target.reparentTo(render)
        self.target.setPos(0.4, -0.4, -0.2)
        self.target.setScale(0.1, 0.1, 0.1)
        self.target.setTransparency(TransparencyAttrib.MAlpha)
        self.target.setAlphaScale(0.8)
    
    def setup_lights(self):
    
        pl = PointLight('pl')
        pl.setColor((1, 1, 1, 1))
        plNP = render.attachNewNode(pl)
        plNP.setPos(0, 0, 0)
        render.setLight(plNP)
        # make shadows less black
        #al = AmbientLight('al')
        #al.setColor((0.2, 0.2, 0.2, 1))
        #alNP = render.attachNewNode(al)
        #render.setLight(alNP)
        positions = [[[0, 0, 3], [0, 0, -1]],
                     [[0, -3, 0], [0, 1, 0]],
                     [[-3, 0, 0], [1, 0, 0]]
                     ]
        # set up directional lights (shadow casting)
        for i in positions:
            dl = Spotlight('dl')
            dl.setColor((1, 1, 1, 1))
            dlNP = render.attachNewNode(dl)
            dlNP.setPos(*i[0]) # unpack the args
            dlNP.lookAt(*i[1])
            dlNP.node().setShadowCaster(True)
            render.setLight(dlNP)
    
    def setup_camera(self):
        self.cam.setPos(-2, -4, 2)
        self.cam.lookAt(0, 0, 0)
    
    def colour_change(self, task):
        dist = sqrt((self.cube.get_x() - self.target.get_x()) ** 2 + (self.cube.get_y() - self.target.get_y()) ** 2 + (self.cube.get_z() - self.target.get_z()) ** 2)
        d2 = 1 - dist
        self.cube.setColorScale(d2, d2, d2, d2)
        return task.cont
        
     
    def move_task(self, task):
        dt = globalClock.get_dt()
        if dt > 0.018:
            print(dt)

        dat, ts = self.dev.read()
        if dat:
            if self.zeroing is None:
                self.zeroing = np.median(dat, axis=0)
            dat = np.array(dat) - self.zeroing
            self.cube.setPos(-dat[-1, 9] * 2, dat[-1, 10] * 2, -dat[-1, 11] * 2)
        return task.cont

if __name__ == '__main__':
    demo = BlamDemo(LslDevice(Hand, nonblocking=False))
    with demo.dev:
        demo.run()