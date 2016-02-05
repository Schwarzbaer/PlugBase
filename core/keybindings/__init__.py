dependencies = []
implements = "keybindings"

from direct.showbase.DirectObject import DirectObject
import sys

global base
global keybindings_manager

def init():
    global keybindings_manager
    keybindings_manager = KeybindingsManager()
    keybindings_manager.test()

class KeybindingsManager(DirectObject):
    def test(self):
        self.accept("f1", base.messenger.send, ["toggle_console", []])
        self.accept("escape", sys.exit)