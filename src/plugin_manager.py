class PluginManager:
    def __init__(self, startup=True):
        #FIXME: Implement
        pass
    
    # ---------------------------------------------------------------
    # Internal helpers
    
    def _get_dependencies(self, plugin_name):
        #FIXME: Implement
        pass
    
    def _get_dependants(self, plugin_name, only_actives=True):
        #FIXME: Implement
        pass
    
    def _get_extenders(self, interface_name, only_actives=True):
        #FIXME: Implement
        pass
    
    def _get_extendees(self, interface_name, only_actives=True):
        #FIXME: Implement
        pass
    
    def _add_extender(self, interface_name):
        #FIXME: Implement
        pass
    
    def _remove_extender(self, interface_name):
        #FIXME: Implement
        pass
        
    # ---------------------------------------------------------------
    # Basic functionality

    def load_plugin(self, plugin_name):
        #FIXME: Implement
        pass
    
    def unload_plugin(self, plugin_name, implicit_destroy=True, unload_dependants=True):
        #FIXME: Implement
        pass
    
    def build_plugin(self, interface_name, implementation=None):
        #FIXME: Implement
        pass
    
    def destroy_plugin(self, interface_name):
        #FIXME: Implement
        pass
    
    # ---------------------------------------------------------------
    # Inspection and notification

    def get_loaded_plugins(self):
        #FIXME: Implement
        pass
    
    def get_active_plugins(self):
        #FIXME: Implement
        pass
    
    def get_interface(self, plugin_name):
        #FIXME: Implement
        pass
    
    def set_callback(self, operations=None):
        #FIXME: Implement
        pass
        
    # ---------------------------------------------------------------
    # High-level comfort functions for managing plugins
    
    def load_plugins(self, plugin_list):
        #FIXME: Implement
        pass
    
    def build_plugins(self, plugin_list):
        #FIXME: Implement
        pass
    
    def reload_plugin(self, plugin_name):
        #FIXME: Implement
        pass
    
    def startup(self):
        #FIXME: Implement
        pass
    


--------------------------------------------------------------------------------
[plugins]
build_on_startup = "keybindings,console,python_console,log_console,plugins_console,config_console,debug_tools"

[plugin_dirs]
plugin_name = "path.to.module"

[plugin_precedences]
interface_name = "plugin_1,plugin_2,plugin_3"
--------------------------------------------------------------------------------
