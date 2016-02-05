from importlib import import_module
import ConfigParser

class PluginManager:
    def __init__(self, config_file = None):
        self.plugins = {}
        self.active_plugins = []
        self.startup(config_file)
    
    def startup(self, config_file):
        # Load all plugins
        with open(config_file, "rb") as config_file:
            self.config = ConfigParser.RawConfigParser()
            self.config.readfp(config_file)
        init_on_startup = self.config.get("plugins", "init_on_startup").split(",")
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
        directory = self.config.get("plugin_dirs", plugin_name)
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
