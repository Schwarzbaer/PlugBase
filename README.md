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

How to PlugBase
---------------


TODO
====

Feature of the Week: PluginManager
----------------------------------
* PluginManager overhaul

Small stuff
-----------
* Document modules, especially events sent / accepted by plugins
* Document PlugBase, especially plugin manager, config manager,
  decorators, helper functions
* Remove debug prints from code

Improve existing plugins
------------------------
* console
  * Interpreter %magic
    * Improve docstrings.
    * Improve docstring format, so that there's no more whitespaces
      an the beginning of lines.
    * Add %magic to work with plugins and config vars
      * %plload "plugin_name"
        %plunload "plugin_name"
        %plhelp "plugin_name"
    * Harden %magic commands against wrong commands and similar
      erroneous input.
  * Pull appearance vars from config_manager
  * Integrate pyperclip, checking for import exception.
  * Wait for LUI to catch up, so that these can be implemented
    * Unset focus on input when console hides
    * Implement editing keystrokes (copy, paste, ...)
    * history
      * Track the bottom
      * Should be scrollable by mousewheel
      * Copy to input field / cursor-up for past command
    * "Save selected fields to file"
      * File selection dialogue
      * Flushing items to file
    * Additional tabs
      * Composing and sending events, adding listeners to
        DirectObjects; base.messenger._getEvents()
      * Managing tasks; base.taskMgr.getTasks()
      * Full list of DirectObjects? (look into Messenger.py for how
        to get a list)
      * List of registered events, and verbose output of events going
        through the systen.
      * Lists of, and players for, media assets
        * Integrate the .bam streamer, maybe as its own plugin.
      * List of code snippets (to hook into tasks and events).
    * Interpreter: Input
      * If an input was incomplete, caused a syntax error or
        traceback, it should not be written to history, and the input
        shouldn't be zeroed.
        * Really? What if the interpreter says that it's complete,
          but the user says it isn't? Use the "terminate with empty
          line" thing?
    * integrate jedi
      * Can I get auto-indentation?
	* A keystroke should focus (and add itself to) the entry box.
    * destroy()
* config_manager
  * @call_on_change should closely check its args.
  * Use eval() to give each config value an explicit type.
  * ConfigManager should be a derived class of ConfigParser
  * Check plugin default configs for unspecified values
    (ConfigParser.NoOptionError)
  * Proper exceptions when not finding values
* keybindings
  * Well, actually implement this.
  * Optional menu
* debug tools
  * render.explore()
  * light.showFrustum()

New plugins
-----------
* Core functionality
  * @expose_hooks
  * Move plugin.* to plugbase?
  * can_use plugin var for deferred init()?
* Capabilities checking
  * See GSG API
* Input bindings, mappings and contexts
* Game element flow
* Graphics packages
* Jailed Python Interpreter for game objects
* Scene Loader
  * Assign controllers: findAllMatches("**/=controller"), then
    instantiate the corresponding classes.
* Procedural geometry generator (akin to tessellation shader)
* Trigger system
  https://bitbucket.org/crmardix/worldwakers_pyweek16/src/ee8159c3765bb7f40aa95a874a5d0444c682f851/game/trigger.py?at=default&fileviewer=file-view-default
  <rdb> Basically an action that should happen, or is only able to
        happen, while the player has triggered something in the
        environment - eg. is in a certain location, or so.
  <rdb> A trigger could cause a checkpoint to be marked off and
        saved, or a trigger could be near a door indicating that when
        the player is close enough, he can press E to open the door.
* Logging console
  * Use for regular logging and for debugging / profiling information
  * (Only) Ship logs to server if explicitly requested to do so
* Collaboration tools
  * Sharing assets
  * Drawing board, text storage
  * VoIP
  * Twitch integration

Far future
----------
* ConfigManager
  * Allow for plugin-wide configs (so packaged plugins can ship with
    their own defaults).
  * There should be a hierarchy of config file objects (i.e. plugin,
    framework, game, editor), and changes should be written into the
    appropriate file, usually the topmost one, unless explicitly
    specified otherwise.
  * %cfgreload, %cfgdiff
  