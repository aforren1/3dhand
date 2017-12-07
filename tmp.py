from direct.showbase.ShowBase import ShowBase
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import (AmbientLight, PointLight, Spotlight, 
                          AntialiasAttrib, KeyboardButton)
from math import sqrt
class BlamDemo(ShowBase):
    
    def __init__(self):
        ShowBase.__init__(self)
        
        render.setAntialias(AntialiasAttrib.MMultisample)
        render.setShaderAuto() # gets us shadows
        
        self.load_models()
        self.setup_lights()
        self.setup_camera()
        self.yp_button = KeyboardButton.ascii_key(b'w')
        self.ym_button = KeyboardButton.ascii_key(b's')
        self.xp_button = KeyboardButton.ascii_key(b'a')
        self.xm_button = KeyboardButton.ascii_key(b'd')
        self.zp_button = KeyboardButton.ascii_key(b'q')
        self.zm_button = KeyboardButton.ascii_key(b'e')
        taskMgr.add(self.move_task, 'move')
        taskMgr.add(self.colour_change, 'col')

    def load_models(self):
        self.background_model = loader.loadModel('background') # background.egg
        self.cube = loader.loadModel('cube')
        
        self.background_model.reparentTo(render)
        self.background_model.setScale(0.5, 0.5, 0.5) #TODO: Just make the original 1,1,1
        self.background_model.setPos(0, 0, -1) # Make the intersection 0, 0, 0
        
        # cube is a sanity check -- replace w/ proper obj
        self.cube.reparentTo(render)
        self.cube.setPos(-0.1, 0.2, 0.4)
        self.cube.setScale(0.1, 0.1, 0.1)
        self.cube.setColorScale(1.0,1.0,1.0,1.0)
    
    def setup_lights(self):
    
        pl = PointLight('pl')
        pl.setColor((1, 1, 1, 1))
        plNP = render.attachNewNode(pl)
        plNP.setPos(0, 0, 0)
        render.setLight(plNP)
        # make shadows less black
        al = AmbientLight('al')
        al.setColor((0.2, 0.2, 0.2, 1))
        alNP = render.attachNewNode(al)
        render.setLight(alNP)
        positions = [[[0, 0, 3], [0, 0, -1]],
                     [[0, -3, 0], [0, 1, 0]],
                     [[-3, 0, 0], [1, 0, 0]]
                     ]
        # set up directional lights (shadow casting)
        for i in positions:
            dl = Spotlight('dl')
            dl.setColor((1, 1, 1, 1))
            dlNP = render.attachNewNode(dl)
            dlNP.setPos(*i[0])
            dlNP.lookAt(*i[1])
            dlNP.node().setShadowCaster(True)
            render.setLight(dlNP)
    
    def setup_camera(self):
        self.cam.setPos(-4, -4, 4)
        self.cam.lookAt(0, 0, 0)
    
    def colour_change(self, task):
        dist = sqrt(self.cube.get_x() ** 2 + self.cube.get_y() ** 2 + self.cube.get_z() ** 2)
        print(dist)
        self.cube.setColorScale(dist, dist, dist, dist)
        return task.cont
        
     
    def move_task(self, task):
        x_speed = 0.0
        y_speed = 0.0
        z_speed = 0.0
        speed = 1.0
        is_down = self.mouseWatcherNode.is_button_down
        
        if is_down(self.xp_button):
            x_speed += speed
        if is_down(self.xm_button):
            x_speed -= speed
        x_delta = x_speed * globalClock.get_dt()
        self.cube.set_x(self.cube.get_x() + x_delta)
        
        if is_down(self.yp_button):
            y_speed += speed
        if is_down(self.ym_button):
            y_speed -= speed
        y_delta = y_speed * globalClock.get_dt()
        self.cube.set_y(self.cube.get_y() + y_delta)
        
        if is_down(self.zp_button):
            z_speed += speed
        if is_down(self.zm_button):
            z_speed -= speed
        z_delta = z_speed * globalClock.get_dt()
        self.cube.set_z(self.cube.get_z() + z_delta)
        return task.cont
    
        
demo = BlamDemo()
demo.run()