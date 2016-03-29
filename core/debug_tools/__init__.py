dependencies = []
implements = "debug_tools"
extends = []

from direct.showbase.DirectObject import DirectObject
from panda3d.core import PStatClient

global base
global listener
global plugin_manager

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global listener
    listener = Listener()

def destroy():
    pass

class Listener(DirectObject):
    def __init__(self):
        self.accept("debug_fps", self.set_fps)
        self.accept("debug_connect_to_pstats", PStatClient.connect)
    
    def set_fps(self, state):
        base.setFrameRateMeter(state)
