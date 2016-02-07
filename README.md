PlugBase
========

A plugin system and a set of standard plugins, so that writing a game
consists only of writing the game, and the game is easy to make
completely moddable.

Features
--------

* A Python console to inspect and manipulate the game's state in real
  time, and which in time may evolve into an IDE.
* Configuration management

TODO: existing plugins
----------------------

* console
  * Interpreter %magic
    * Harden %magic commands against wrong commands and similar erroneous
      input.
    * Improve docstrings.
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
      * Composing and sending events, adding listeners to DirectObjects; base.messenger._getEvents()
      * Managing tasks; base.taskMgr.getTasks()
      * Full list of DirectObjects? (look into Messenger.py for how to get a list)
    * Interpreter: Input
      * If an input was incomplete, caused a syntax error or traceback, it
        should not be written to history, and the input shouldn't be zeroed.
        * Really? What if the interpreter says that it's complete, but the user
          says it isn't? Use the "terminate with empty line" thing?
    * integrate jedi
* config_manager
  * Get @call_on_change to work
  * Check plugin default configs for unspecified values (ConfigParser.NoOptionError)
  * Proper exceptions when not finding values
  * What about non-string type values? We've got tuples of floats already!
	* Must be asserted in the setter functions.
* keybindings
  * Well, actually implement this.
  * Optional menu

TODO
----

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
  <rdb> Basically an action that should happen, or is only able to happen, while the player has triggered something in the environment - eg. is in a certain location, or so.
  <rdb> A trigger could cause a checkpoint to be marked off and saved, or a trigger could be near a door indicating that when the player is close enough, he can press E to open the door.
* Logging console
  * Use for regular logging and for debugging / profiling information
  * (Only) Ship logs to server if explicitly requested to do so

  LUI NOTES
  ---------
  
# Design elements
#   Text style
#     label.add(text="This", font_size=20, margin_top=-6, color=(0.4,0.2,1.0))
#   Text alignment
#     my_text.center_vertical = True
#     Or center_horizontal
#     my_obj.left = 10, right aligned: my_obj.right = 10
#   Layout
#     LUIVerticalLayout(spacing = 10, use_dividers = True)
#   LUIFrame: FIXME
#   LUISprite(parent, "blank", "skin", x=0, y=0, w=123, h=456, color=(bla))
#   Margin as in CSS: top, right, bottom, left
#     margin = (0, 0, 0, 0)
#   Padding too. Also, a single number for all sides is possible.
#     padding = 10
#   color affects text color
#     color=(0.4,0.0,0.0, 1.0)
# Other notes
#   Be notified if child has changed its attributes
#     .bind("child_changed", xxx)
# Questions
#   Can I build from master again?
#   How do I unset focus on input field?
#   How do I get the cursor's position in an InputField / TextField?
#     ._cursor_index, but that is not exposed yet
#   What should I call when the window's / frame's size has changed?
#   How do I make elements expand to the full available height or width?
#   How do I create a skin?
#   How do I design dividers and borders?
#     By now, you can't influence borders.
#   How do I use the cut buffer to C-v content into the InputField?
#   What about Pos1/End?
# Open needs
#   Text wrapping
#   .bind("parent_changed", my_function_that_does_the_design)
#     May not be a need after all
#   LUITextArea, because LUIInputField is single-line only.




# Questions and Wants
#   Where do fonts come from, and how do I set them?
#   Why do elements and layouts have a different way of building the tree?
#   What kind of pattern follows to create a class that encapsulates a tree of GUI elements?
#     Subclassing the container, then using attributes to store widgets
#   Colors; how do they work?
#     Barely, and on few elements. Better use sprites.
#       But then how do I create complex elements via inheritance?
#     Why does a container, which has no color, darken the background?
#       It's the default skin.
#   Is there a complete list of design-related attributes?
#     What about not-design-related ones?
#   How come buttons take only three sprites (left, middle, right), while other
#     elements take a 3x3 grid? Also, are the middle ones nx1 strips, or tiles?
