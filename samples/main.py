#!/usr/bin/env python

import os
import plugbase

game_dir = os.path.dirname(__file__)
config_file = game_dir + "game.cfg"
print("Game config file is %s" % (repr(config_file), ))
plugbase.run(config_file)
