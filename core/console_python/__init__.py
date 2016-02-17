"""A Python console for more interactive game development than
Panda3D offers by itself.

Interface:
* console: The actual interpreter and GUI
  * Actually, nothing of this is meant for public consumption ATM.
* consolew_magic: A set of self-documenting extensions of the
    console's functionality, in the form of %magic commands.
  * add_magic (not implemented):
  * remove_magic (also not implemented):
"""

dependencies = ["console"]
implements = "python_console"

from LUILabel import LUILabel
from LUIButton import LUIButton

from console import Console, ConsoleCommands

global base
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter
global config_manager
global console # Do I even want this?
global console_magic

def init():
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

def destroy():
    global console
    console.destroy()
    console = None # FIXME: It's a DirectObject, though
