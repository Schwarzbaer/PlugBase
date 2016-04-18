from importlib import import_module#, reload
from ConfigParser import SafeConfigParser
from direct.showbase.DirectObject import DirectObject
import traceback
from weakref import WeakSet

global config_manager

class PluginNotFound(Exception):
    pass

class PluginNotLoadable(Exception):
    pass

class PluginNotBuildable(Exception):
    pass

class PluginNotLoaded(Exception):
    pass

class PluginNotBuilt(Exception):
    pass

class PluginManager:
    def __init__(self, config_files = None):
        self.plugins = {}
        self.active_plugins = []
        self.extenders = {} # "extender": set(extendees
        global config_manager
        config_manager = ConfigManager(config_files)
        self.startup()
    
    def _get_extenders(self, extendee):
        extenders = []
        for extender, extendees in self.extenders.iteritems():
            if extendee in extendees:
                extenders.append(extender)
        return extenders
    
    def _get_extendees(self, plugin_name):
        assert plugin_name in self.extenders.keys(), "Extender not registered"
        all_extendees = self.extenders[plugin_name]
        return [extendee for extendee in all_extendees if extendee in self.active_plugins]
    
    def _add_extender(self, extender, extendees):
        assert extender not in self.extenders.keys(), "Extender already registered"
        self.extenders[extender] = set(extendees)
    
    def _remove_extender(self, extender):
        assert extender in self.extenders.keys(), "Extender not registered"
        del self.extenders[extender]
    
    def _get_dependants(self, root_plugin_name, only_actives=True):
        # TODO: Respect only_actives
        dependants = [root_plugin_name]
        dependants_added = True
        while dependants_added:
            dependants_added = False
            for plugin_name, plugin in self.plugins.iteritems():
                if not only_actives or plugin_name in self.active_plugins:
                    plugin_deps = plugin.dependencies
                    if any([dep in dependants for dep in plugin_deps]):
                        if plugin_name not in dependants:
                            dependants.append(plugin_name)
                            dependants_added = True
        del dependants[dependants.index(root_plugin_name)]
        return dependants            
    
    def startup(self):
        """Try to build all plugins that are named in the config
        file's build_on_startup."""
        # Load all plugins
        build_on_startup = config_manager.get("plugins", "build_on_startup").split(",")
        loaded_plugins, unloadable_plugins = self.load_plugins(build_on_startup)
        built_plugins, unbuildable_plugins = self.build_plugins(loaded_plugins)
        if built_plugins:
            print("Built plugins  : %s" % (", ".join(built_plugins) ,))
        if unbuildable_plugins:
            print("Could not build: %s" % (", ".join(unbuildable_plugins) ,))
        if unloadable_plugins:
            print("Could not load : %s" % (", ".join(unloadable_plugins) ,))
    
    def load_plugin(self, plugin_name):
        """Load a plugin.
        Throws PluginNotLoadable if the plugin can't be imported"""
        assert plugin_name not in self.plugins.keys(), "Plugin already loaded"
        directory = config_manager.get("plugin_dirs", plugin_name)
        try:
            plugin = import_module(directory)
        except SyntaxError:
            # TODO: Embed actual exception and stacktrace
            raise PluginNotLoadable()
        self.plugins[plugin_name] = plugin
    
    def load_plugins(self, plugin_list):
        loaded_plugins = []
        unloadable_plugins = []
        for plugin_name in plugin_list:
            try:
                self.load_plugin(plugin_name)
                loaded_plugins.append(plugin_name)
            except PluginNotLoadable:
                # FIXME: Embedded exception and stack trace (once
                # those exist; there's a TODO in load_plugin about
                # that) should be communicated
                unloadable_plugins.append(plugin_name)
        return loaded_plugins, unloadable_plugins
    
    def unload_plugin(self, plugin_name, implicit_destroy=True, unload_dependants=True):
        if plugin_name not in self.plugins.keys():
            raise PluginNotLoaded()
        if not implicit_destroy:
            assert plugin_name not in self.active_plugins, "Plugin is still active"
        else:
            # First the dependents, then the plugin itself
            deps = self._get_dependants(plugin_name, only_actives=True)
            for dep in deps:
                self.destroy_plugin(dep)
            if plugin_name in self.active_plugins:
                self.destroy_plugin(plugin_name)
        if unload_dependants:
            deps = self._get_dependants(plugin_name, only_actives=False)
            for dep in deps:
                self.unload_plugin(dep, unload_dependants=False)
        del self.plugins[plugin_name]
    
    def reload_plugin(self, plugin_name):
        if plugin_name in self.plugins.keys():
            self.plugins[plugin_name].destroy()
            self.plugins[plugin_name] = reload(self.plugins[plugin_name])
            self.build_plugin(plugin_name)
        else:
            raise PluginNotLoaded
    
    # Building and destroying

    def build_plugin(self, plugin_name):
        if plugin_name not in self.plugins.keys():
            raise PluginNotLoaded
        try:
            deps = self.plugins[plugin_name].dependencies
            if all([d in self.active_plugins for d in deps]):
                self.plugins[plugin_name].build(self)
                self.active_plugins.append(plugin_name)
                self._add_extender(plugin_name, self.plugins[plugin_name].extends)
                for extender in self._get_extenders(plugin_name):
                    self.plugins[extender].extend(plugin_name)
                for extendee in self._get_extendees(plugin_name):
                    self.plugins[plugin_name].extend(extendee)
                return True
            else:
                return False
        except Exception as e:
            # FIXME: Add original exception
            raise PluginNotBuildable
    
    def build_plugins(self, plugin_list):
        built_plugins = []
        unbuildable_plugins = []
        left_to_build = [pn for pn in plugin_list]
        continue_building = True
        
        while continue_building:
            for idx in range(len(left_to_build)):
                plugin_name = left_to_build[idx]
                try:
                    built = self.build_plugin(plugin_name)
                    if built:
                        built_plugins.append(plugin_name)
                        del left_to_build[idx]
                        break
                except PluginNotBuildable, PluginNotLoaded:
                    unbuildable_plugins.append(plugin_name)
                    del left_to_build[idx]
                    break
            else:
                continue_building = False
        return built_plugins, left_to_build + unbuildable_plugins
    
    def destroy_plugin(self, plugin_name):
        deps = self._get_dependants(plugin_name, only_actives=True)
        # TODO: Also destroy plugins that depend on this one
        if plugin_name not in self.active_plugins:
            raise PluginNotBuilt
        for extendee in self._get_extendees(plugin_name):
            self.plugins[plugin_name].unextend(extendee)
        for extender in self._get_extenders(plugin_name):
            self.plugins[extender].unextend(plugin_name)
        self.plugins[plugin_name].destroy()
        del self.active_plugins[self.active_plugins.index(plugin_name)]

    # TODO: destroy_pligins
    
    def get_loaded_plugins(self):
        return self.plugins.keys()
    
    def get_active_plugins(self):
        return self.active_plugins
    
    def get_interface(self, plugin_name):
        return self.plugins[plugin_name].interface


class ConfigManager(DirectObject):
    def __init__(self, config_files):
        DirectObject.__init__(self)
        self.config = SafeConfigParser()
        read_files = self.config.read(config_files)
        unread_files = []
        for f in config_files:
            if f not in read_files:
                unread_files.append(f)
        if len(unread_files) > 0:
            print("Couldn't read config files %s." % (", ".join(unread_files), ))
        for config_file in reversed(config_files):
            if config_file in read_files:
                self.writeback_file = config_file
                print("Will write config to %s" % (config_file, ))
                break
        else:
            print("No config file to write back to found!")
            self.writeback_file = None
        
        self.update_callbacks = {}
        self.accept("change_config_value", self.set)
        self.accept("config_write", self.write)

    def sections(self):
        return self.config.sections()

    def items(self, section):
        return self.config.items(section)

    def get(self, section, variable):
        value = eval(self.config.get(section, variable))
        return value

    def set(self, section, variable, value):
        self.config.set(section, variable, repr(value))
        if (section, variable) in self.update_callbacks:
            for callback in self.update_callbacks[(section, variable)]:
                callback(value)
        base.messenger.send("config_value_changed", [section, variable, value])

    def write(self):
        if self.writeback_file is not None:
            with open(self.writeback_file, "wb") as f:
                self.config.write(f)
        else:
            #FIXME: Exception, your honor!
            print("Still no config to write to known!")

    def destroy(self):
        self.config.close()
    
    def _register_callback(self, section, variable, function):
        key = (section, variable)
        if key not in self.update_callbacks:
            # TODO: After moving to Py3-only, weakref.WeakMethod should
            # be used here, so as not to keep objects alive when this is
            # the last reference to it (via the method).
            self.update_callbacks[key] = set()
        self.update_callbacks[key].add(function)

class ConfigValue(object):
    def __init__(self, section, variable, update_callback = None):
        self.section = section
        self.variable = variable
        if update_callback is not None:
            config_manager._register_callback(section, variable, update_callback)

    def get(self):
        return config_manager.get(self.section, self.variable)

    def set(self, value):
        config_manager.set(self.section, self.variable, value)

    # TODO: Implement
    def __delete__(self, obj):
        raise NotImplementedError("config_manager lacks removal capability.")
        # config_manager.remove(self.section, self.variable)

def get_config_value(section, variable, value_type = str):
    return value_type(config_manager.get(section, variable))

def set_config_value(section, variable, value):
    config_manager.set_value(section, variable, value)

def get_config_variables(section):
    return config_manager.items(section)

def get_config_sections():
    return config_manager.sections()

class call_on_change(DirectObject):
    def __init__(self, *args):
        if len(args) == 3 and all([isinstance(arg, str) for arg in args]):
            self.patterns = [args]
        else: # FIXME: Check elements!
            self.patterns = args
        self.objects_to_call = WeakSet()
        #print(self.section, self.variable, self.method_name)
        self.accept("config_value_changed", self.change_event_filter)
    
    def __call__(self, constructor):
        def inner_func(*args, **kwargs):
            wrapped_object = constructor(*args, **kwargs)
            self.objects_to_call.add(wrapped_object)
            #print(len(self.objects_to_call), repr(wrapped_object))
            return wrapped_object
        return inner_func
        
    def change_event_filter(self, change_section, change_variable, value):
        #print("@call_on_change(%s, %s, %s, %s)" % (repr(self),
        #                                           repr(change_section),
        #                                           repr(change_variable),
        #                                           repr(value)))
        for (section, variable, method_name) in self.patterns:
            if (change_section, change_variable) == (section, variable):
                #print("Sending on...")
                for wrapped_object in self.objects_to_call:
                    #print("Sending on to %s" % (repr(wrapped_object)))
                    getattr(wrapped_object, method_name)(value)
            
class configargs(object):
    """
    Decorator that will add default values for kwargs which are read
    from the config file, unless values for the kwarg in question are
    already supplied in the method call.

    @configargs(foo = ("foosection", "foovar")})
    """
    def __init__(self, *args, **default_kwargs):
        global config_manager
        self.default_kwargs = default_kwargs

    def __call__(self, wrapped_func):
        global config_manager
        def inner_func(*args, **kwargs):
            for key in self.default_kwargs.keys():
                if key not in kwargs.keys():
                    variable_description = self.default_kwargs[key]
                    if len(variable_description) == 2:
                        kwargs[key] = config_manager.get(*variable_description)
                    else:
                        kwargs[key] = variable_description[2](config_manager.get(variable_description[0], variable_description[1]))
            return wrapped_func(*args, **kwargs)
        return inner_func
