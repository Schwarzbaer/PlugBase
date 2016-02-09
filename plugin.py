import weakref

from importlib import import_module
from ConfigParser import SafeConfigParser
from direct.showbase.DirectObject import DirectObject

global config_manager

class PluginManager:
    def __init__(self, config_files = None):
        self.plugins = {}
        self.active_plugins = []
        global config_manager
        config_manager = ConfigManager(config_files)
        self.startup()
    
    def startup(self):
        # Load all plugins
        init_on_startup = config_manager.get_value("plugins", "init_on_startup").split(",")
        for plugin_name in init_on_startup:
            self.load_plugin(plugin_name)
        left_to_init = self.plugins.keys()
        
        # Init them.
        # FIXME: Can we get some topological sorting in here? You know, "the right way"?
        while True:
            loaded_one = False
            left_to_init_post = []
            for plugin_name in left_to_init:
                inited = self.init_plugin(plugin_name)
                loaded_one = loaded_one or inited
                if not inited:
                    left_to_init_post.append(plugin_name)
                else:
                    print("Inited %s" % (plugin_name, ))
            left_to_init = left_to_init_post
            if (len(left_to_init) == 0) or (not loaded_one):
                break
        
        if left_to_init:
            print("Couldn't load: %s" % (", ".join(left_to_init) ,))
    
    def load_plugin(self, plugin_name):
        directory = config_manager.get_value("plugin_dirs", plugin_name)
        plugin = import_module(directory)
        plugin.plugin_manager = self
        self.plugins[plugin_name] = plugin
    
    def init_plugin(self, plugin_name):
        # FIXME: assert that plugin is loaded.
        #   Have a switch to auto-load it if it isn't.
        deps = self.plugins[plugin_name].dependencies
        if all([d in self.active_plugins for d in deps]):
            self.plugins[plugin_name].init()
            self.active_plugins.append(plugin_name)
            return True
        else:
            return False
    
    def get_loaded_plugins(self):
        return self.plugins.keys()
    
    def get_active_plugins(self):
        return self.active_plugins


class ConfigManager(DirectObject):
    def __init__(self, config_files):
        self.config = SafeConfigParser()
        read_files = self.config.read(config_files)
        unread_files = []
        for f in config_files:
            if f not in read_files:
                unread_files.append(f)
        if len(unread_files) > 0:
            print("Couldn't read config files %s." % (", ".join(unread_files), ))
        self.accept("change_config_value", self.set_value)

    def get_value(self, section, variable):
        value = self.config.get(section, variable)
        return value

    def set_value(self, section, variable, value):
        self.config.set(section, variable, str(value))
        base.messenger.send("config_value_changed", [section, variable, value])

    def destroy(self):
        self.config.close()

def get_config_value(section, variable, value_type = str):
    return value_type(config_manager.get_value(section, variable))

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
                        kwargs[key] = config_manager.get_value(*variable_description)
                    else:
                        kwargs[key] = variable_description[2](config_manager.get_value(variable_description[0], variable_description[1]))
            return wrapped_func(*args, **kwargs)
        return inner_func
