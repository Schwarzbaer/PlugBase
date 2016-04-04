"""A Python console for more interactive game development than
Panda3D offers by itself.

Interface:
* add_magic(magic_name, method): Do not use directly. Instead, derive
  classes from core.console_python.MagicDonor, decorate its methods
  with core.console_python.tokenize_magic (zero arguments), and
  create an instance of that class.
* remove_magic (not implemented)
"""

dependencies = ["console"]
implements = "python_console"
extends = []

from LUILabel import LUILabel
from LUIButton import LUIButton

from console import Console, ConsoleCommands

global base
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter
global config_manager
global console # Do I even want this?
global console_magic
global interface


def build(pm):
    global plugin_manager
    plugin_manager = pm
    from plugin import config_manager as cfg_mgr
    global config_manager
    config_manager = cfg_mgr
    global console_magic
    console_magic = ConsoleCommands(plugin_manager, config_manager)
    global console
    console = Console(interpreter_locals = dict(pm = plugin_manager,
                                                cm = config_manager,
                                                console_command = console_magic))
    plugin_manager.get_interface("console").add_console(LUIButton(text = "Python"), console.gui_window.console_frame)
    global interface
    interface = ConsoleInterface()


def destroy():
    global console
    console.destroy()
    console = None # FIXME: It's a DirectObject, though


class ConsoleInterface:
    def add_magic(self, name, method):
        global console_magic
        setattr(console_magic, name, method)

    def remove_magic(self, name):
        global console_magic
        delattr(console_magic, name)

class MagicDonor:
    def __init__(self):
        self._magic_commands = [method_name
                                for method_name in dir(self)
                                if not method_name.startswith('_')]
        self._give_magic()
        
    def _give_magic(self):
        console_interface = plugin_manager.get_interface("python_console")
        for method_name in self._magic_commands:
            # TODO: Log method_name
            method = getattr(self, method_name)
            console_interface.add_magic(method_name, method)

    def _take_magic(self):
        console_interface = plugin_manager.get_interface("python_console")
        for method_name in self._magic_commands:
            # TODO: Log method_name
            console_interface.remove_magic(method_name)
