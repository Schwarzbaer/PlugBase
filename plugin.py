import weakref

from importlib import import_module
from ConfigParser import SafeConfigParser
from direct.showbase.DirectObject import DirectObject

global config_manager

class PluginNotFound(Exception):
    pass

class PluginNotLoadable(Exception):
    pass

class PluginNotInitializable(Exception):
    pass

class PluginNotLoaded(Exception):
    pass

class PluginNotInitialized(Exception):
    pass

class PluginManager:
    def __init__(self, config_files = None):
        self.plugins = {}
        self.active_plugins = []
        global config_manager
        config_manager = ConfigManager(config_files)
        self.startup()
    
    def startup(self):
        # Load all plugins
        init_on_startup = config_manager.get("plugins", "init_on_startup").split(",")
        loaded_plugins, unloadable_plugins = self.load_plugins(init_on_startup)
        inited_plugins, uninitable_plugins = self.init_plugins(loaded_plugins)
        if inited_plugins:
            print("Initialized plugins : %s" % (", ".join(inited_plugins) ,))
        if uninitable_plugins:
            print("Could not initialize: %s" % (", ".join(uninitable_plugins) ,))
        if unloadable_plugins:
            print("Could not load      : %s" % (", ".join(unloadable_plugins) ,))
    
    def load_plugin(self, plugin_name):
        directory = config_manager.get("plugin_dirs", plugin_name)
        try:
            plugin = import_module(directory)
        except SyntaxError:
            raise PluginNotLoadable()
        plugin.plugin_manager = self
        self.plugins[plugin_name] = plugin
    
    def load_plugins(self, plugin_list):
        loaded_plugins = []
        unloadable_plugins = []
        for plugin_name in plugin_list:
            try:
                self.load_plugin(plugin_name)
                loaded_plugins.append(plugin_name)
            except PluginNotLoadable:
                unloadable_plugins.append(plugin_name)
        return loaded_plugins, unloadable_plugins
    
    def unload_plugin(self, plugin_name):
        self.plugins[plugin_name].destroy()
        del self.plugins[plugin_name]
    
    def reload_plugin(self, plugin_name):
        self.unload_plugin(plugin_name)
        self.load_plugin(plugin_name)
    
    def init_plugin(self, plugin_name):
        # FIXME: assert that plugin is loaded.
        #   Have a switch to auto-load it if it isn't.
        try:
            deps = self.plugins[plugin_name].dependencies
            if all([d in self.active_plugins for d in deps]):
                self.plugins[plugin_name].init()
                self.active_plugins.append(plugin_name)
                return True
            else:
                return False
        except:
            raise PluginNotInitializable
    
    def init_plugins(self, plugin_list):
        inited_plugins = []
        uninitable_plugins = []
        left_to_init = [pn for pn in plugin_list]
        continue_initing = True
        
        while continue_initing:
            for idx in range(len(left_to_init)):
                plugin_name = left_to_init[idx]
                try:
                    inited = self.init_plugin(plugin_name)
                    if inited:
                        inited_plugins.append(plugin_name)
                        del left_to_init[idx]
                        break
                except PluginNotInitializable:
                    uninitable_plugins.append(plugin_name)
                    del left_to_init[idx]
                    break
            else:
                continue_initing = False
        return inited_plugins, left_to_init + uninitable_plugins
            

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
        self.config.set( section, variable, repr(value))
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

def get_config_value(section, variable, value_type = str):
    return value_type(config_manager.get(section, variable))

def set_config_value(section, variable, value):
    config_manager.set_value(section, variable, value)

class call_on_change(DirectObject):
    def __init__(self, *args):
        if len(args) == 3 and all([isinstance(arg, str) for arg in args]):
            self.patterns = [args]
        else: # FIXME: Check elements!
            self.patterns = args
        self.objects_to_call = weakref.WeakSet()
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
