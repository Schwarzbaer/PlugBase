Plugin API
----------

A plugin is a module that
* must have an 'implements' attribute, which is a string
* may have a 'dependencies' attribute, which is a list of strings
* may have an 'extends' attribute, which is a list of strings
  * must then have an .extend() function, which takes a plugin name
    as argument
  * must then have an .unextend() function, which takes a plugin name
    as argument
* must have a .build() function, which takes a PluginManager instance
  as argument
* must have a .destroy() function, which takes no arguments

Referencing a Plugin in Configuration
-------------------------------------

* The plugin's implement string defines what kind of interface the
  plugin implements. This is the interface name.
* The actual implementation can also have an individual name, to
  disambiguate several plugins that implement the same interface.
  This is the plugin name.
* The game's (or the framework's) configuration file should, in the
  section plugin_dirs, associate the plugin name with a string that
  contains the plugin's location in Python module path notation.
* The config may (and the framework's config does) have a section
  plugins with a variable build_on_startup, which contains a string
  that is a comma-separated list of plugin names, all of which will
  be attempted to be loaded and built on startup.

Plugin Life Cycle
-----------------

The plugin lifecycle consists of four stages.

load_plugin
* Import module
* Register extenders
* Plugin is not loaded and inactive
build
* Call .build()
* Let other active plugins extend this
* Let this plugin extend other active ones
* plugin is now loaded and active
destroy_plugin
* Unextend
* Call .destroy()
* plugin is now loaded and inactive
unload_plugin
* Unregister extenders
* Remove reference to module
* plugin is now not loaded


Plugin Manager
--------------

* load_plugins
* build_plugins
* reload_plugin
  * If the plugin is active, destroy it.
  * retain a reference to the module
  * unload it
  * call reload(module)
  * load the plugin
  * If it was active, build it.
* startup
  * In the config file, in the section [plugins], in the variable
    "build_on_startup", specify a string (enclosed by parantheses)
    consisting of a comma-separated list of plugin types. These
    plugins will be loaded and built on startup.
