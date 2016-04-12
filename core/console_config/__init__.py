from direct.showbase.DirectObject import DirectObject
import datetime
import re

from panda3d.lui import LUIObject, LUIVerticalLayout, LUIHorizontalLayout
from LUIScrollableRegion import LUIScrollableRegion
from LUIButton import LUIButton
from LUIInputField import LUIInputField
from LUIFormattedLabel import LUIFormattedLabel

from plugin import get_config_value, set_config_value, get_config_variables, get_config_sections

dependencies = ['console']
implements = 'config_console'
# extends = ['python_console']
extends = []

global base
global plugin_manager
global interface

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global interface
    interface = ConfigConsole()
    plugin_manager.get_interface("console").add_console(LUIButton(text = "Config"), interface.get_gui())

def destroy():
    global interface
    interface.destroy()
    interface = None

def extend(plugin_name):
    pass

def unextend(plugin_name):
    pass

class ConfigConsole(DirectObject):
    def __init__(self):
        self.setup_gui()
    
    def setup_gui(self):
        self.gui_root = LUIScrollableRegion()
        self.gui_root.width = "100%"
        self.gui_root.height = "100%"
        self.gui_root.set_debug_name("gui_root")

        self.gui_layout = LUIVerticalLayout(parent = self.gui_root,
                                            spacing = 2)
        self.gui_layout.width = "100%"
        self.gui_layout.height = "100%"
        self.gui_layout.set_debug_name("gui_layout")

        self._show()

    def get_gui(self):
        return self.gui_root
    
    def destroy(self):
        # TODO: Implement
        pass

    def _show(self):
        for section in get_config_sections():
            section_header = LUIFormattedLabel()
            section_header.set_debug_name("section_header")
            section_header.add(section, font_size=20, color=(0.2, 0.6, 1.0))
            self.gui_layout.add(section_header)
            for var, value in get_config_variables(section):
                
                var_line = LUIObject()
                var_line.set_debug_name("var_line")
                var_line.width = "100%"
                self.gui_layout.add(var_line)
                var_layout = LUIHorizontalLayout(parent = var_line)
                var_layout.width = "100%"
                
                var_name = LUIFormattedLabel()
                var_name.set_debug_name("var_name")
                var_name.add(var, color=(0.6, 0.6, 0.6))
                var_layout.add(var_name, "15%")
                
                var_value = LUIFormattedLabel()
                var_value.set_debug_name("var_value")
                var_value.add(value, color=(0.93, 0.93, 0.93))
                var_layout.add(var_value, "85%")
        self.gui_root.ls()
