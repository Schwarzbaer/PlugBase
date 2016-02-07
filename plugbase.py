#!/usr/bin/env python

# TODO
# Move Plugin_Manager in here?
# Add "can_use" as plugin variable, which means that if possible, this plugin should be init()ed after the named ones, and that it should be informed of them having been started, so that it can expose special behaviour; i.e. the console supporting catching config variable events.
# * The example is pointless, as plugins can accept events even when they will never be emitted.  
# Write config_manager plugin
# * Have PluginManager .close() config before loading any plugin
#   * Apparently pm should also use readfp() instead?
# * Have config_manager read/write configs, emit value changes as events,
#   and .close() on destroy()
# Write @expose_hook to allow for easy hooking into a plugin's
#   functionality.
# Write @configargs to add default values for kwargs where not
#   overridden by them being explicitly stated.
# Document how to write a plugin.

import os

from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData
#from direct.showbase.DirectObject import DirectObject

from plugin import PluginManager

# This will be overwritten by ShowBase and PlugBase. It's just here
# to suppress Eclipse errors.
global base
global globalClock
#global plugin_manager

# All interaction with plugins will go through here.
class PlugBase(ShowBase):
    def __init__(self, config_file = None, underlay_default_conf = True):
        # The basics
        ShowBase.__init__(self)
        base.disableMouse()

        #builtins.plugin_manager = PluginManager()
        #plugin_manager.load_plugins()
        configs = []
        if underlay_default_conf:
            framework_conf = os.path.abspath(__file__) + "core.cfg"
            configs.append(framework_conf)
        if config_file is not None:
            configs.append(config_file)
        self.plugin_manager = PluginManager(configs)

# Setup
# The application object is stored globally for easy access in an
# interactive Python interpreter session.
app = None

def run(config_file = None):
    loadPrcFileData("", "sync-video #t")
    global app
    if config_file is None:
        app = PlugBase()
    else:
        app = PlugBase(config_file = config_file)
    app.run()

if __name__ == '__main__':
    run()
