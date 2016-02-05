dependencies = []
implements = "config_manager"

import ConfigParser

global base
global config_manager
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter

def init():
    global config_manager
    config_manager = ConfigManager()

def destroy():
    global config_manager
    config_manager.destroy()
    config_manager = None

class ConfigManager(object):
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read('game.cfg')

    def get_value(self, section, variable):
        value = self.config.get(section, variable)
        return value

    def set_value(self, section, variable, value):
        self.config.set(section, variable, value)
        base.messenger.send("config_value_changed", [section, variable, value])

    def destroy(self):
        self.config.close()

def get_config_value(section, variable, value_type = str):
    return value_type(config_manager.get_value(section, variable))

def set_config_value(section, variable, value):
    config_manager.set_value(section, variable, value)

# FIXME: Now how to implement this?? It should cause the decorated
# method to receive pre-filtered events.
class call_on_change(object):
    def __init__(self, section, variable):
        self.section = section
        self.variable = variable
    
    def __call__(self, wrapped_func):
        pass

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
