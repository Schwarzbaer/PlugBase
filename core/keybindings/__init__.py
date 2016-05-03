implements = "keybindings"

from direct.showbase.DirectObject import DirectObject
import sys

global base
global keybindings_manager
global plugin_manager

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global keybindings_manager
    keybindings_manager = KeybindingsManager()
    keybindings_manager.test()

class KeybindingsManager(DirectObject):
    def test(self):
        self.accept("f1", base.messenger.send, ["toggle_console", []])
        self.accept("escape", sys.exit)
        self.cursor_pos = 0
        # TODO: Remove these debug funcs
        #self.accept("control-arrow_left", base.messenger.send, ["cursor_skip_left", []])
        #self.accept("control-arrow_right", base.messenger.send, ["cursor_skip_right", []])
        self.accept("f2", base.messenger.send, ["cursor_skip_left", []])
        self.accept("f3", base.messenger.send, ["cursor_skip_right", []])
    
    def cursor_pos_change(self, delta):
        self.cursor_pos += delta
        base.messenger.send("set_cursor_pos", [self.cursor_pos])
