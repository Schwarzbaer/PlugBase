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

global base
global plugin_manager
global interface
global tab_ref

def build(pm):
    global plugin_manager
    plugin_manager = pm
    global interface
    interface = ConfigConsole()
    global tab_ref
    tab_ref = plugin_manager.get_interface("console").add_console(LUIButton(text = "Config"), interface.get_gui())

def destroy():
    global tab_ref
    plugin_manager.get_interface("console").remove_console(tab_ref)
    tab_ref = None
    global interface
    interface.destroy()
    interface = None

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
            GUISection(section, self.gui_layout)
        
        self.gui_root.ls()

    def get_gui(self):
        return self.gui_root
    
    def destroy(self):
        # TODO: Implement
        pass

    def _show(self):
        self.gui_root.ls()


class GUISection:
    def __init__(self, section, layout):
        header_color = ConfigValue("console_config", "color_section", self.update_header_color)
        
        self.section_header = LUILabel(text=section, font_size=20, color=header_color.get())
        #self.section_header.height = "100%"
        self.section_header.width = "100%"
        self.section_header.set_debug_name("section_header")
        layout.add(self.section_header)
        
        for var, _ in get_config_variables(section):
            layout.add(GUIVariableCell(section, var))
    
    def update_header_color(self, value):
        self.section_header.color = value


class GUIVariableCell(LUIObject):
    def __init__(self, section, variable):
        super(GUIVariableCell, self).__init__()
        self.set_debug_name("var_line")
        #self.height = "100%"
        self.width = "100%"
        elem_height = False
        
        self.color_variable = ConfigValue("console_config", "color_variable", self.change_var_name_color)
        self.color_value = ConfigValue("console_config", "color_value", self.change_var_value_color)
        self.mode = 0 # 0 for display, 1 for entry
        
        self.var_layout = LUIHorizontalLayout(parent = self)
        #if elem_height: self.var_layout.height = "100%"
        self.var_layout.width = "100%"

        self.var_name = LUIFormattedLabel()
        if elem_height: self.var_name.height = "100%"
        self.var_name.width = "100%"
        self.var_name.set_debug_name("var_name")
        self.var_name.add(variable, color=self.color_variable.get())
        self.var_layout.add(self.var_name, "15%")
        
        self.value = ConfigValue(section, variable, self.value_updated)
        self.var_value = LUILabel()
        self.var_value.set_debug_name("var_value")
        if elem_height: self.var_value.height = "100%"
        #self.var_value.width = "100%"
        self.var_value.set_text(repr(self.value.get()))
        self.var_value.solid = True
        self.var_value.bind("click", self.toggle_mode)
        self.var_layout.add(self.var_value)
        
        self.var_value_entry = LUIInputField()
        self.var_value_entry.set_debug_name("var_value_input")
        if elem_height: self.var_value_entry.height = "100%"
        #self.var_value_entry.width = "100%"
        self.var_value_entry.margin = (-6, 0, 0, -6)
        self.var_value_entry.value = repr(self.value.get())
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
            self.var_value_entry.request_focus()
        else:
            self.mode = 0
            self.var_value.show()
            #self.var_value.parent.width = "85%"
            self.var_value_entry.hide()

    def enter_new_value(self, event):
        value = eval(self.var_value_entry.get_value())
        self.value.set(value)
        self.toggle_display()

    def value_updated(self, value):
        self.var_value.set_text(repr(value))
        self.var_value_entry.value = repr(value)

    def change_var_name_color(self, value):
        self.var_name.color = value

    def change_var_value_color(self, value):
        self.var_value.color = value
