from direct.showbase.DirectObject import DirectObject
import datetime
import re

from direct.task import Task
from panda3d.lui import LUIObject, LUIVerticalLayout, LUIHorizontalLayout
from LUIScrollableRegion import LUIScrollableRegion
from LUIButton import LUIButton
from LUIInputField import LUIInputField
from LUIFormattedLabel import LUIFormattedLabel

from plugin import get_config_variables
from core.console_python import MagicDonor
from core.console_python.console import tokenize_magic

dependencies = ['console']
implements = 'plugins_console'
extends = []

global base
global plugin_manager
global interface

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global interface
    interface = PluginsConsole()
    plugin_manager.get_interface("console").add_console(LUIButton(text = "Plugins"), interface.get_gui())
    # TODO: Python console %magic

def destroy():
    global interface
    interface.destroy()
    interface = None
    # TODO: Undo Python console %magic

def extend(plugin_name):
    pass

def unextend(plugin_name):
    pass

class PluginsConsole:
    def __init__(self):
        self.setup_gui()
        self.update_task = base.taskMgr.do_method_later(0.25, self.update_gui, "Show me what you got.")
    
    def setup_gui(self):
        self.gui_root = LUIObject()
        self.gui_root.width = "100%"
        self.gui_root.height = "100%"
        self.gui_root.set_debug_name("DEBUG gui_root")

    def update_gui(self, *whatever):
        available = [plugin for plugin, _ in get_config_variables("plugin_dirs")]
        loaded = plugin_manager.get_loaded_plugins()
        active = plugin_manager.get_active_plugins()
        not_loaded = set(available) - set(loaded)
        inactive = set(loaded) - set(active)
        if False:
            print("Unloaded: " + ", ".join(not_loaded))
            print("Inactive: " + ", ".join(inactive))
            print("Active  : " + ", ".join(active))
        return Task.cont

    def get_gui(self):
        return self.gui_root
        
    def destroy(self):
        # TODO: remove GUI
        base.taskMgr.remove(self.update_task)
