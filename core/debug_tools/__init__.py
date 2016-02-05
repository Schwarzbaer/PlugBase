dependencies = []
implements = "debug_tools"

from direct.showbase.DirectObject import DirectObject
from panda3d.core import PStatClient

global base
global listener

def init():
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
