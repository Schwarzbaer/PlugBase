from direct.showbase.DirectObject import DirectObject
import datetime
import re

from panda3d.lui import LUIObject, LUIVerticalLayout, LUIHorizontalLayout
from LUIScrollableRegion import LUIScrollableRegion
from LUIButton import LUIButton
from LUIInputField import LUIInputField
from LUIFormattedLabel import LUIFormattedLabel
from LUILabel import LUILabel
from LUIInputField import LUIInputField

from plugin import get_config_value, set_config_value, get_config_variables, get_config_sections,\
    ConfigValue

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

        for section in get_config_sections():
            section_header = LUIFormattedLabel()
            section_header.set_debug_name("section_header")
            section_header.add(section, font_size=20, color=(0.2, 0.6, 1.0))
            self.gui_layout.add(section_header)
            for var, _ in get_config_variables(section):
                cell = GUICell(section, var)
                self.gui_layout.add(cell.root_obj)

    def get_gui(self):
        return self.gui_root
    
    def destroy(self):
        # TODO: Implement
        pass

    def _show(self):
        self.gui_root.ls()

class GUICell:
    def __init__(self, section, variable):
        self.mode = 0 # 0 for display, 1 for entry
        self.value = ConfigValue(section, variable, self.value_updated)
        self.root_obj = LUIObject()
        self.root_obj.set_debug_name("var_line")
        self.root_obj.width = "100%"
        self.var_layout = LUIHorizontalLayout(parent = self.root_obj)
        self.var_layout.width = "100%"

        self.var_name = LUIFormattedLabel()
        self.var_name.set_debug_name("var_name")
        self.var_name.add(variable, color=(0.6, 0.6, 0.6))
        self.var_layout.add(self.var_name, "15%")
        
        self.var_value = LUILabel()
        #self.var_value = LUIFormattedLabel()
        self.var_value.set_debug_name("var_value")
        self.var_value.set_text(str(self.value.get()))
        #self.var_value.add(str(self.value.get()), color=(0.93, 0.93, 0.93))
        self.var_value.solid = True
        self.var_value.bind("click", self.toggle_mode)
        self.var_layout.add(self.var_value)#, "85%")
        
        self.var_value_entry = LUIInputField()
        self.var_value_entry.set_debug_name("var_value_input")
        self.var_value_entry.set_value(self.value.get())
        self.var_value_entry.bind("enter", self.enter_new_value)
        self.var_layout.add(self.var_value_entry)#, "85%")
        
        self.var_value_entry.hide()

    def toggle_mode(self, event):
        self.toggle_display()
    
    def toggle_display(self):
        if self.mode == 0:
            self.mode = 1
            self.var_value.hide()
            self.var_value.parent.width = 0
            self.var_value_entry.show()
        else:
            self.mode = 0
            self.var_value.show()
            #self.var_value.parent.width = "85%"
            self.var_value_entry.hide()

    def enter_new_value(self, event):
        self.value.set(self.var_value_entry.get_value())
        self.toggle_display()

    def value_updated(self, value):
        self.var_value.set_text(str(value))
        self.var_value_entry.set_value(value)
