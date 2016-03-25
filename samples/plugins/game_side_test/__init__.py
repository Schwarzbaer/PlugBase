"""An example of how a plugin module should look like.

This is simply a demonstration of how to write plugins. Every plugin
for PlugBase is a Python module, and has two attributes, dependencies
and implements, and two functions, build() and destroy().

implements is a string that describes the functionality implemented
by the plugin, and with it also implies the interface that should be
used to interact with the plugin and its classes. Currently, no
documentation to that end exists, beyond the implementations
themselves.

dependencies is a list of strings that each represent the
functionality of a plugin that this plugin depends on. If, for
instance, this plugin had dependencies = ["foo"], then it would only
be initialized once PlugBase had made sure that a plugin is active
that implements the functionality foo.

Once a plugin is loaded and its dependencies are initialized, then
the plugin itself is initialized. First, the plugin manager sets the
module's attribute plugin_manager to iself, as a way for the plugin
to interact with the rest of the plugin infrastructure. Then the
plugin's build() is called. The plugin now should do what is
necessary to get up and running, and ready for other plugins that
depend on it to be initialized.

Finally, when the plugin is unloaded, destroy() is called. The plugin
should tear down everything with regards to it, including setting
module references to its objects to None, so that they can be garbage
collected.

Please make sure to include a docstring like this in your module, so
that it can be inspected with the Python console's tools. The first
line will be used as a short description, the second line is expected
to be empty, and the rest will be used as a detailed description.
"""

dependencies = []
implements = ""

global plugin_manager

def build():
    print("Game-side plugin initialized")

def destroy():
    print("Game-side plugin destroyed")
