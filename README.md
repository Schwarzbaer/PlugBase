PlugBase
========

A plugin system and a set of standard plugins, so that writing a game
consists only of writing the game, and the game is easy to make
completely moddable.

PlugBase features:
* Plugin loading and automatically ordered initialization
* Centralized configuration management
* A Python console to inspect and manipulate the game's state in real
  time, and which in time may evolve into an IDE.

PlugBase depends on Panda3D (http://www.panda3d.org/) and LUI
(https://github.com/tobspr/LUI). It uses git-flow to manage the code
repository (http://danielkummer.github.io/git-flow-cheatsheet/).

How to PlugBase
---------------

PlugBase ships with a self-documentation system, and the interactive
console to access it. When you run plugbase.py or the sample in
samples, press F1 to open the console, and follow the instructions
given.

For an example on how to implement a plugin, take a look at the
samples' plugin game_side_test.

Also do take a look at core.cfg and samples/game.cfg to see how the
system is bootstrapped via configuration. 
