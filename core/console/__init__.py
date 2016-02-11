dependencies = ["keybindings"]
implements = "console"

import re
import shlex

from console import Console

global base
global console # Do I even want this?
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter
global config_manager # Set by the plugin_manager, used from within the InteractiveInterpreter

def init():
    from plugin import config_manager as cfg_mgr
    global config_manager
    config_manager = cfg_mgr
    global console
    console = Console(interpreter_locals = dict(pm = plugin_manager,
                                                cm = config_manager,
                                                console_command = ConsoleCommands()))

def destroy():
    global console
    console.destroy()
    console = None

# FIXME: Add arg for further explanation based on isinstance(exception, ...)
class ArgumentNotEvaluable(Exception):
    def __init__(self, token):
        self.token = token
    
    def __str__(self):
        return "Problem encountered on token %s" % (repr(self.token), )

kwarg_token = re.compile("^([a-zA-Z]\w*)=(.+)$")

class tokenize_magic:
    """Decorator class doc string"""
    def __init__(self):
        pass
    
    def __call__(self, wrapped_func):
        """Doc string for the decorators __call__"""
        def inner_func(obj, magic_text):
            args, kwargs = self.tokenize(magic_text)
            return wrapped_func(obj, *args, **kwargs)
        inner_func.__doc__ = wrapped_func.__doc__
        return inner_func
    
    def tokenize(self, magic_text):
        args = []
        kwargs = {}
        tokens = shlex.split(magic_text, posix = False)
        for token in tokens:
            kwarg_groups = kwarg_token.match(token)
            if kwarg_groups is None:
                # There's no left-hand side indicating that it's a kwarg
                try:
                    value = eval(token)
                except (SyntaxError, NameError):
                    raise ArgumentNotEvaluable(token)
                args.append(value)
            else:
                # Left-hand side says that it's a kwarg
                try:
                    value = eval(kwarg_groups.groups()[1])
                except (SyntaxError, NameError):
                    raise ArgumentNotEvaluable(kwarg_groups.groups()[1])
                kwargs[kwarg_groups.groups()[0]] = value
        return args, kwargs

class ConsoleCommands:
    """Embedded Python console. use %help for a list of commands, 
    %help "help" for details, and %syntax for an explanation of
    the console's %magic commands.
    """
    def __init__(self, command_prefix = "%", max_command_length = None):
        if max_command_length is None:
            self.max_command_length = 2 + max([len(m) for m in dir(self)
                                               if callable(getattr(self, m)) and m[0] != '_'])
        else:
            self.max_command_length = max_command_length
        self.command_prefix = command_prefix
        
    @tokenize_magic()
    def help(self, command = None):
        """Print help text. Use '%help "command" for more specific help.
        
        There should be a longer explanation here, but I really can't think of
        anything more to say about this.
        """
        if command is None:
            for method in [m for m in dir(self)
                           if callable(getattr(self, m)) and m[0] != '_']:
                doc = getattr(self, method).__doc__
                brief_doc = doc.splitlines()[0]
                print("%s%s%s%s" % (self.command_prefix,
                                    method,
                                    " "*(self.max_command_length-len(method)),
                                    brief_doc))
        elif hasattr(self, command):
            full_doc = getattr(self, command).__doc__
            main_doc = full_doc.split("\n")[2:]
            print("\n".join(main_doc))
        else:
            print("Unknown command: %s" % (command, ) )

    @tokenize_magic()
    def syntax(self):
        """Explanation of the console's syntax for %magic commands.
        
        An example:
            %command "string_argument" bound_variable 42 kwarg="foo"

        Commands take a space-separated list of arguments, which can
        be either non-keyword or keyword arguments (just like in
        Python). Strings have to be enclosed in quotation marks, as
        bare words get interpreted as variables. Numbers get
        interpreted as you would expect. Keywords may consist of
        letters, digits and underdashes, but must start with a
        letter.
        Internally, everything after the %command name gets tokenized
        by shlex, checked by a regex for whether it is a kwarg, and
        then eval'd to yield the final value. Then those values are
        sorted based on whether they're args or kwargs, then passed
        to the class that implements %magic.
        """
        print("\n".join(self.syntax.__doc__.split("\n")[2:]))

    @tokenize_magic()
    def testargs(self, *args, **kwargs):
        """helper function to test argument-passing to %commands.
        
        This method prints the arguments given to it, and their type.
        """
        for arg in args:
            print(repr(arg) + " (" + repr(type(arg).__name__) + ")")
        for key, value in kwargs.iteritems():
            print(key + " = " + repr(value) + " (" + repr(type(value).__name__) + ")")
    
    @tokenize_magic()
    def sendev(self, event_name, *args):
        """Send an event.
        
        Example: %sendev("debug_fps", True)"""
        base.messenger.send(event_name, list(args))
        print("Sent event %s with arguments %s" % (event_name, ", ".join([repr(arg) for arg in args])))

    # PluginManager-related

    @tokenize_magic()
    def pllist(self):
        """Show list of loaded / active plugins.
        
        Shows which plugins are loaded, and which ones are loaded and
        active.
        """
        
        loaded = plugin_manager.get_loaded_plugins()
        active = plugin_manager.get_active_plugins()
        for plugin in loaded:
            if plugin in active:
                print(plugin + " (active)")
            else:
                print(plugin + " (loaded)")

    @tokenize_magic()
    def cfglist(self, *args):
        """Show configuration data.
        
        Usage: %cfglist ["section" ["variable"]]
        
        If no section is provided, this command will print a list of
        sections. If a section is provided, it will show the
        variables in that section. If both a section and a variable
        are provided, it will show just that variable.
        """
        if len(args) == 0:
            for section in config_manager.sections():
                print(section)
        elif len(args) == 1:
            for item, value in config_manager.items(args[0]):
                print(str(item) + " = " + str(value))
        elif len(args) == 2:
            print(config_manager.get(args[0], args[1]))

    @tokenize_magic()
    def cfgset(self, section, variable, value):
        """Set a configuration variable.
        
        Usage: %cfgset section variable value
        """
        config_manager.set(section, variable, value)
    
    @tokenize_magic()
    def cfgwrite(self):
        """Write changes back to config file.
        
        Write changed configuration values into the file that has
        been determined to be the appropriate one by virtue of
        being the last one in the list of config files that actually
        exists."""
        config_manager.write()

    @tokenize_magic()
    def plload(self, plugin_name):
        """Load and initialize a plugin.
        
        Usage: %plload plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # can't be found or inited.
        # FIXME: Also, how about a just-load option?
        plugin_manager.load_plugin(plugin_name)
        plugin_manager.init_plugin(plugin_name)

    @tokenize_magic()
    def plinit(self, plugin_name):
        """Initialize a loaded but inactive plugin.
        
        Usage: %plinit plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # can't be inited. Maybe there should also be a check whether
        # it is even loaded in the first place, or already active?
        plugin_manager.load_plugin(plugin_name)
        plugin_manager.init_plugin(plugin_name)
