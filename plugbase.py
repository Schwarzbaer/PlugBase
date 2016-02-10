#!/usr/bin/env python

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
            framework_conf = os.path.dirname(os.path.abspath(__file__)) + "/core.cfg"
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
