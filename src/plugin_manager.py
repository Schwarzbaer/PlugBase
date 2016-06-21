from config_manager import ConfigManager

class PluginManager:
    """
    Relevant config:

        [plugins]
        build_on_startup = "keybindings,console,python_console,log_console,plugins_console,config_console,debug_tools"
        
        [plugin_dirs]
        plugin_name = "path.to.module"
        
        [plugin_precedences]
        interface_name = "plugin_1,plugin_2,plugin_3"
    """
    def __init__(self, startup=True, config_manager=None):
        self.loaded_plugins = {}  # "plugin_name": <plugin_module>
        self.active_plugins = {}  # "interface_name": "plugin_name"
        self.active_extensions = {}  # "interface_name": set(["interface_name"])
        if config_manager is None:
            self.config_manager = ConfigManager()
        else:
            self.config_manager = config_manager
        if startup:
            self.startup()

    # ---------------------------------------------------------------
    # Internal helpers

    def plugin_dependencies(self, plugin):
        """Return the list of interfaces that this plugin (of the
        given name) depends on to be active to function itself."""
        assert plugin in self.loaded_plugins, "Plugin not loaded"
        if hasattr(self.loaded_plugins[plugin], "dependencies"):
            return self.loaded_plugins[plugin].dependencies
        else:
            return []

    def plugin_dependants(self, plugin, only_actives=True, return_interfaces=False):
        assert plugin in self.loaded_plugins, "Plugin not loaded"
        interface = self.loaded_plugins[plugin].implements
        if only_actives:
            other_plugins = self.active_plugins.values()
        else:
            other_plugins = self.loaded_plugins
        if return_interfaces:
            return [self.loaded_plugins[other_plugin].implements
                    for other_plugin in other_plugins
                    if interface in self.plugin_dependencies(other_plugin)]
        else:
            return [other_plugin
                    for other_plugin in other_plugins
                    if interface in self.plugin_dependencies(other_plugin)]

    def implementations(self, interface):
        return [plugin
                for plugin in self.loaded_plugins
                if self.loaded_plugins[plugin].implements == interface]

    def interface_dependencies(self, interface):
        assert interface in self.active_plugins, "Plugin not active"
        plugin = self.active_plugins[interface]
        return self.plugin_dependencies(plugin)

    def interface_dependants(self, interface, only_actives=True, return_plugins=False):
        assert interface in self.active_plugins, "Plugin not active"
        plugin = self.active_plugins[interface]
        return self.plugin_dependants(plugin, only_actives, not return_plugins)

    def plugin_extendees(self, plugin):
        """What interfaces can the (loaded) plugin of the given name extend?"""
        assert plugin in self.loaded_plugins, "Plugin not loaded"
        if hasattr(self.loaded_plugins[plugin], "extends"):
            return self.loaded_plugins[plugin].extends
        else:
            return []

    def active_extendees(self, interface):
        return self.active_extensions[interface]

    def active_extenders(self, interface):
        return [extender
                for extender, extendees in self.active_extensions.iteritems()
                if interface in extendees]

    def loaded_extenders(self, interface):
        """Returns the list of loaded plugins that can extent the given interface."""
        return [extender
                for extender in self.loaded_plugins
                if interface in self.plugin_extendees(extender)]

    def loaded_extendees(self, interface):
        return [plugin
                for plugin, plugin_module in self.loaded_plugins.items()
                if plugin_module.implements == interface]

    def add_active_extension(self, extender, extendee):
        if extender not in self.active_extensions:
            self.active_extensions[extender] = set()
        self.active_extensions[extender].add(extendee)

    def remove_active_extension(self, extender, extendee):
        self.active_extensions[extender].remove(extendee)

    # ---------------------------------------------------------------
    # Basic functionality

    def load_plugin(self, plugin):
        """
        * Import module
        * Register extenders
        * Plugin is not loaded and inactive
        """
        # FIXME: Implement
        pass

    def build_plugin(self, interface, implementation=None):
        """
        * Call .build()
        * Let other active plugins extend this
        * Let this plugin extend other active ones
        * plugin is now loaded and active
        """
        assert interface not in self.active_plugins, "Interface is already being implemented"
        if implementation in None:
            num_implementations = len(self.implementations(interface))
            assert num_implementations > 0, "No implementation of interface loaded"
            assert num_implementations < 2, "Ambiguous interface, multiple implementations present"

        # FIXME: This needs a proper exception, and maybe information about the missing deps.
        assert all([dep in self.active_plugins
                    for dep in self.plugin_dependencies(plugin)]), "Unsatisfied dependencies"

    def destroy_plugin(self, interface_name):
        """
        * Unextend
        * Call .destroy()
        * plugin is now loaded and inactive
        """
        # FIXME: Implement
        pass

    def unload_plugin(self, plugin_name, implicit_destroy=True, unload_dependants=True):
        """
        * Unregister extenders
        * Remove reference to module
        * plugin is now not loaded
        """
        # FIXME: Implement
        pass

    # ---------------------------------------------------------------
    # Inspection and notification

    def get_loaded_plugins(self):
        # FIXME: Implement
        pass

    def get_active_plugins(self):
        # FIXME: Implement
        pass

    def get_interface(self, plugin_name):
        # FIXME: Implement
        pass

    def set_callback(self, operations=None):
        # FIXME: Implement
        pass

    # ---------------------------------------------------------------
    # High-level comfort functions for managing plugins

    def load_plugins(self, plugin_list):
        # FIXME: Implement
        pass

    def build_plugins(self, plugin_list):
        # FIXME: Implement
        pass

    def reload_plugin(self, plugin_name):
        """
        * If the plugin is active, destroy it.
        * retain a reference to the module
        * unload it
        * call reload(module)
        * load the plugin
        * If it was active, build it.
        """
        # FIXME: Implement
        pass

    def startup(self):
        """
        In the config file, in the section [plugins], in the variable
        "build_on_startup", specify a string (enclosed by parantheses)
        consisting of a comma-separated list of plugin types. These
        plugins will be loaded and built on startup.
        """
        # FIXME: Implement
        pass
