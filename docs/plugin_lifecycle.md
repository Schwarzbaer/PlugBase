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



Helper functions
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
