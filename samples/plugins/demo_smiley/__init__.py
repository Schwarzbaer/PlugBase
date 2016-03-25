dependencies = []
implements = "demo_smiley"

from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task

from plugin import configargs, call_on_change

global base
global globalClock
global plugin_manager

global smiley

def build():
    global smiley
    smiley = DemoSmiley()

def destroy():
    global smiley
    smiley.destroy()
    smiley = None

@call_on_change(("demo_smiley", "rotation_speed", "set_rotation_speed"),
                ("demo_smiley", "roll_speed", "set_roll_speed"))
class DemoSmiley(DirectObject):
    @configargs(rotation_speed = ("demo_smiley", "rotation_speed", float),
                roll_speed = ("demo_smiley", "roll_speed", float))
    def __init__(self, rotation_speed = 1.0, roll_speed = 1.0):
        DirectObject.__init__(self)
        self.rotation_speed = rotation_speed
        self.roll_speed = roll_speed

        base.camera.set_pos(0, -5, 0)
        base.camera.look_at(0, 0, 0)
    
        self.model = base.loader.loadModel("models/smiley")
        self.model.reparent_to(base.render)
        
        #self.accept("config_value_changed", self.config_value_changed)
        self.task = base.taskMgr.add(self.rotate, "rotate_smiley")
    
    def rotate(self, task):
        dt = globalClock.getDt()
        self.model.set_h(self.model, self.rotation_speed * 360.0 * dt)
        self.model.set_p(self.model, self.roll_speed * 360.0 * dt)
        return Task.cont
    
    def config_value_changed(self, section, variable, value):
        if (section, variable) == ("demo_smiley", "rotation_speed"):
            self.rotation_speed = value
    
    def set_rotation_speed(self, value):
        #print("Setting rotation speed to %f" % (value, ))
        self.rotation_speed = value
    
    def set_roll_speed(self, value):
        #print("Setting roll speed to %f" % (value, ))
        self.roll_speed = value
    
    def destroy(self):
        base.taskMgr.remove(self.task)
        self.model.remove_node()
