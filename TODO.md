Feature of the Week: PluginManager
----------------------------------
* Refactor load/build/extend/unextend/destroy/unload life cycle.
* Properties that relate to ConfigManager values, i.e.:
    StringProperty(42, "section", "variable", validate=lambda x:True, 
                   change_handler=lambda x: pass)
  Also have:
    GenericProperty(<default>, ..., process=lambda x:x)
  where process takes the string coming from the ConfigManager and
  can be turned into any kind of data structure.
* PluginManager should treat plugin.extends / .extend() / .unextend()
  as optional.

Small stuff
-----------
* "Could not build" needs to output error and trace
* Implement .destroy() in console, console_log.LogConsole and others
* console_python.MagicDonor needs a method to undo its transplants
* Document modules, especially events sent / accepted by plugins
* Document PlugBase, especially plugin manager, config manager,
  decorators, helper functions
* Remove debug prints from code
* Move %pl* magic into console_plugins code

Towards 1.0
-----------
* console
  * Interpreter %magic
    * Improve docstrings.
    * Improve docstring format, so that there's no more whitespaces
      an the beginning of lines.
    * Harden %magic commands against wrong commands and similar
      erroneous input.
  * Pull appearance vars from config_manager
  * Integrate pyperclip, checking for import exception.
  * "Save selected fields to file"
    * File selection dialogue
    * Flushing items to file
  * Improvements depending on improvements to LUI
    * Unset focus on input when console hides
    * Implement editing keystrokes (copy, paste, ...)
    * history
      * Track the bottom
      * Should be scrollable by mousewheel
      * Copy to input field / cursor-up for past command
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
      * List and exemplars of objects in pools.
        * Create inspection interfaces, i.e. for ModelPool
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
* config_manager
  * @call_on_change should closely check its args.
  * Use eval() to give each config value an explicit type.
  * ConfigManager should be a derived class of ConfigParser
  * Check plugin default configs for unspecified values
    (ConfigParser.NoOptionError)
  * Proper exceptions when not finding values
  * Try not to use Panda3D's events
* keybindings
  * Well, actually implement this.
  * Optional menu
* debug tools
  * render.explore()
  * light.showFrustum()
  * NP.showBounds()
  * The equivalent for colliders and physics bodies
  * Tool for temporarily taking over the camera
    * Create a camera that colocates with the currently chosen
      camera, takes over its DisplayBuffer, can be controlled
      manually, and at the end restores the original state.
* Logging console
  * Use for regular logging and for debugging / profiling information
  * Write to graphical window, stdout/stderr and/or file
  * logrotate and/or purge old logs
  * (Only) Ship logs to server if explicitly requested to do so
  * Make appearance configurable at runtime
* Config console
* Core functionality
  * @expose_hooks
  * Move plugin.* to plugbase?
  * can_use plugin var for deferred build()?
* Capabilities checking
  * See GSG and GraphicsPipe API.
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
* Collaboration tools
  * Sharing assets
  * Drawing board, text storage
  * VoIP
  * Twitch integration
* Code hygiene
  * optionalize DirectObject in plugin.py
  * add logging
  * insure Py2 / Py3 compliance
  * run() deadlocks browser, so when there's a replacement idiom,
    use that one.
  * Normalize directory structure

Beyond 1.0
----------
* ConfigManager
  * Allow for plugin-wide configs (so packaged plugins can ship with
    their own defaults).
  * There should be a hierarchy of config file objects (i.e. plugin,
    framework, game, editor), and changes should be written into the
    appropriate file, usually the topmost one, unless explicitly
    specified otherwise.
  * %cfgreload, %cfgdiff
  * Maybe provide descriptors for using config values as attributes?
* Mega-consoles
  * Make console tabs drag&droppable, so that they be added, removed,
    and moved between consoles, even broken out into windows of their
    own and added back into others.
* Plugin downloader
  * Provide central plugin repository
  * Support author- and reviewer-signing
