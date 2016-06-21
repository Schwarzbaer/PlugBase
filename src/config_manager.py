from configparser import SafeConfigParser


GAME_CONFIG = 3
FRAMEWORK_CONFIG = 2
PLUGIN_CONFIG = 1


class ConfigManager:
    def __init__(self, config_files=None):
        self.config = SafeConfigParser()
        if config_files is not None:
            read_files = self.config.read(config_files)
        else:
            config_files = []
        unread_files = []
        for f in config_files:
            if f not in read_files:
                unread_files.append(f)
        if len(unread_files) > 0:
            # FIXME: Log instead.
            print("Couldn't read config files %s." % (", ".join(unread_files),))

        self.update_callbacks = {}
        # TODO: This reguires an argument on whether to activate Panda3D
        # integration. If so, we need a DirectObject here to accept events.
        if False:
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

    def write(self):
        if self.writeback_file is not None:
            with open(self.writeback_file, "wb") as f:
                self.config.write(f)
        else:
            # FIXME: Exception, your honor!
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
