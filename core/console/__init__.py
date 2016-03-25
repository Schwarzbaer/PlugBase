dependencies = ["keybindings"]
implements = "console"

from direct.showbase.DirectObject import DirectObject
from panda3d.lui import LUIRegion, LUIInputHandler

from LUISkin import LUIDefaultSkin
from LUITabbedFrame import LUITabbedFrame

global base
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter
global interface

def build():
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
    
        tabbed_frame = LUITabbedFrame(parent = region.root)
        tabbed_frame.pos = (0, 0)
        tabbed_frame.width = "100%"
        tabbed_frame.height = "100%"
        tabbed_frame.margin = 20
        tabbed_frame.style = LUITabbedFrame.FS_raised
        self.frame = tabbed_frame

        self.visible = False
        self.frame.hide()
        self.accept("toggle_console", self._toggle_visibility)

    def destroy(self):
        self.frame = None

    def _toggle_visibility(self):
        if self.visible:
            # Hide Console
            self.visible = False
        else:
            # Show console
            self.visible = True
        self.frame.set_visible(self.visible)

    def add_console(self, button, window):
        self.frame.add(button, window)
