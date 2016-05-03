dependencies = ["keybindings"]
implements = "console"

from direct.showbase.DirectObject import DirectObject
from panda3d.lui import LUIRegion, LUIInputHandler

from LUISkin import LUIDefaultSkin
from LUITabbedFrame import LUITabbedFrame

from plugin import ConfigValue

global base
global plugin_manager
global interface

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global interface
    interface = ConsoleFrame()

def destroy():
    global interface
    interface.destroy()
    interface = None

class ConsoleFrame(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        skin = LUIDefaultSkin()
        skin.load()
    
        region = LUIRegion.make("LUI", base.win)
        handler = LUIInputHandler()
        base.mouseWatcher.attach_new_node(handler)
        region.set_input_handler(handler)
        
        self.width = ConfigValue("console", "width", self._set_width)
        self.height = ConfigValue("console", "height", self._set_height)
        self.alpha = ConfigValue("console", "alpha", self._set_alpha)
        
        self.frame = LUITabbedFrame(parent = region.root)
        self.frame.pos = (0, 0)
        self.frame.width = "{}%".format(int(self.width.get() * 100))
        self.frame.height = "{}%".format(int(self.height.get() * 100))
        self.frame.margin = 20
        self.frame.style = LUITabbedFrame.FS_raised
        self.frame.alpha = self.alpha.get()

        self.visible = False
        self.frame.hide()
        self.accept("toggle_console", self._toggle_visibility)

    def destroy(self):
        self.frame = None

    def _toggle_visibility(self):
        if self.visible:
            # Hide Console
            self.visible = False
            self.frame.trigger_event("unexpose")
        else:
            # Show console
            self.visible = True
            self.frame.trigger_event("expose")
        self.frame.set_visible(self.visible)

    def _set_width(self, value):
        self.frame.width = "{}%".format(int(value * 100))

    def _set_height(self, value):
        self.frame.height = "{}%".format(int(value * 100))

    def _set_alpha(self, value):
        self.frame.alpha = value

    def add_console(self, button, window):
        return self.frame.add(button, window)

    def remove_console(self, button):
        self.frame.remove(button)
