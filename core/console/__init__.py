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

dependencies = ["keybindings"]
implements = "console"

from console import Console, ConsoleCommands

global base
global console # Do I even want this?
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter

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

def destroy():
    global console
    console.destroy()
    console = None # FIXME: It's a DirectObject, though
