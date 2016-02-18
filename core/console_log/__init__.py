from direct.showbase.DirectObject import DirectObject
import datetime
import re

from panda3d.lui import LUIObject, LUIVerticalLayout, LUIHorizontalLayout
from LUIScrollableRegion import LUIScrollableRegion
from LUIButton import LUIButton
from LUIInputField import LUIInputField
from LUIFormattedLabel import LUIFormattedLabel

dependencies = ["console"]
implements = "log_console"

global base
global plugin_manager
global interface

def init():
    global interface
    interface = LogConsole()
    plugin_manager.get_interface("console").add_console(LUIButton(text = "Log"), interface.get_gui())
    
def destroy():
    global interface
    interface.destroy()
    interface = None

DEBUG = 0
INFO = 1
WARNING = 2
ERROR = 3
loglevel_to_string = ["DEBUG", "INFO", "WARNING", "ERROR"]
log_color = {0: (0.5, 0.5, 0.5),
             1: (1.0, 1.0, 1.0),
             2: (1.0, 1.0, 0.0),
             3: (1.0, 0.0, 0.0)}

class LogConsole(DirectObject):
    def __init__(self):
        DirectObject.__init__(self)
        self.log_entries = []
        #super(LogConsole, self).__init__()
        self.num_loglevels = 4
        self.loglevel = 0
        self.filter_regex = re.compile("")
        self.setup_gui()
        self.accept("log-event", self._log)
    
    def setup_gui(self):
        self.gui_root = LUIObject()
        self.gui_root.width = "100%"
        self.gui_root.height = "100%"
        self.gui_root.set_debug_name("DEBUG gui_root")

        self.gui_layout = LUIVerticalLayout(parent = self.gui_root,
                                            spacing = 2)
        self.gui_layout.width = "100%"
        self.gui_layout.height = "100%"
        self.gui_layout.set_debug_name("DEBUG gui_layout")

        self.log_history_region = LUIScrollableRegion()
        self.log_history_region.width = "100%"
        self.log_history_region.height = "100%"
        self.log_history_region.set_debug_name("DEBUG log_history_region")
        self.gui_layout.add(self.log_history_region, "*")
        
        self.log_history = LUIVerticalLayout(parent = self.log_history_region.content_node,
                                         spacing = 2)
        self.log_history.width = "100%"
        #self.log_history.height = "100%"
        self.log_history.set_debug_name("DEBUG log_history")
        
        self.filter_bar = LUIHorizontalLayout(parent = self.gui_layout.cell("?"))
        self.filter_bar.width = "100%"
        self.filter_loglevel = LUIButton(parent = self.filter_bar.cell("20%"),
                                         text = loglevel_to_string[self.loglevel],
                                         color = log_color[self.loglevel])
        self.filter_loglevel.width = "100%"
        self.filter_loglevel.bind("click", self._toggle_loglevel)
        self.filter_string = LUIInputField(parent = self.filter_bar.cell("80%"))
        self.filter_string.width = "100%"
        self.filter_string.top = 1
        self.filter_string.left = 5
        self.filter_string.bind("enter", self._set_filter_string)

    def get_gui(self):
        return self.gui_root
    
    def _log(self, loglevel, message):
        now = datetime.datetime.now()

        history_entry = LUIObject()
        history_entry.set_debug_name("DEBUG history_entry")
        history_entry.width = "100%"
        
        history_entry_layout = LUIHorizontalLayout(parent = history_entry)
        history_entry_layout.width = "100%"
        
        history_entry_timestamp = LUIFormattedLabel()
        history_entry_timestamp.add(now.strftime("%H:%M:%S.%f"))
        history_entry_layout.add(history_entry_timestamp, "15%")

        history_entry_loglevel = LUIFormattedLabel()
        history_entry_loglevel.add(loglevel_to_string[loglevel], color = log_color[loglevel])
        history_entry_layout.add(history_entry_loglevel, "15%")

        history_entry_message = LUIFormattedLabel()
        for line in message.split("\n"):
            history_entry_message.add(line, font_size = 15, color = log_color[loglevel])
            history_entry_message.newline()
        history_entry_layout.add(history_entry_message, "70%")

        self.log_history.add(history_entry, "?")
        self.log_entries.append((now, loglevel, message, history_entry))
        self.log_history_region.scroll_to_bottom()

    def _toggle_loglevel(self, lui_event):
        self.loglevel = (self.loglevel + 1) % self.num_loglevels
        self.filter_loglevel.color = log_color[self.loglevel]
        self.filter_loglevel.text = loglevel_to_string[self.loglevel]
        self._refilter()

    def _set_filter_string(self, lui_event):
        filter_string = self.filter_string.get_value()
        self.filter_regex = re.compile(filter_string)
        self._refilter()

    def _refilter(self):
        for (timestamp, loglevel, message, history_entry) in self.log_entries:
            filters = [loglevel >= self.loglevel,
                       self.filter_regex.search(message) is not None]
            print(filters)
            if all(filters):
                history_entry.show()
            else:
                history_entry.hide()
