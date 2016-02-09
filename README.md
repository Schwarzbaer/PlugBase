PlugBase
========

A plugin system and a set of standard plugins, so that writing a game
consists only of writing the game, and the game is easy to make
completely moddable.

PlugBase features:
* A Python console to inspect and manipulate the game's state in real
  time, and which in time may evolve into an IDE.
* Centralized configuration management

How to PlugBase
---------------



TODO: Right now
---------------
* Document modules, especially events sent / accepted by plugins
* Document PlugBase, especially plugin manager, config manager,
  decorators, helper functions
* Remove debug prints from code

TODO: Existing plugins
----------------------

* console
  * Interpreter %magic
    * Improve docstrings.
    * Improve docstring format, so that there's no more whitespaces
      an the beginning of lines.
    * Add %magic to work with plugins and config vars
      * %cfgget ["section" ["variable"]]
        %cfgset "section" "variable" value
        %cfgsave
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
    * Interpreter: Input
      * If an input was incomplete, caused a syntax error or
        traceback, it should not be written to history, and the input
        shouldn't be zeroed.
        * Really? What if the interpreter says that it's complete,
          but the user says it isn't? Use the "terminate with empty
          line" thing?
    * integrate jedi
* config_manager
  * @call_on_change should closely check its args.
  * Check plugin default configs for unspecified values
    (ConfigParser.NoOptionError)
  * Write changed configs back to file (and track what actually did
    change)
  * Proper exceptions when not finding values
  * What about non-string type values? We've got tuples of floats
    already!
	* Must be asserted in the setter functions.
* keybindings
  * Well, actually implement this.
  * Optional menu
* debug tools
  * render.explore()
  * light.showFrustum()

TODO: New plugins
-----------------

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
