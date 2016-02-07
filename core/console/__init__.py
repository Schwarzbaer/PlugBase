dependencies = ["keybindings"]
implements = "console"

# TODO
# When enough text is entered so that the scroll bar appears, it
#   should be on bottom position, and track it when text is
#   entered.
# A keystroke should focus (and add the keystroke to) the entry
#   box.
# Finish destroy()
# Improve the Interpreter
# Add more relevant locals / globals to the interpreter
# Add shorthands to the interpreter input, akin to %paste
# References to base should be replaced by window-specific
#   references, as not using ShowBase will probably make base vanish,
#   too.
# IDEificatioin
#   History
#   Input should not be limited to a single line
#   Tab completion should exist
#     https://github.com/davidhalter/jedi
#   There should be help with indentation (also jedi)
#   Saving code snippets
# Many resize() operations (i.e. text placements) should only be done
#   if the Y size of the window actually has changed
# Add support for frames on the canvas, because nothing says "simple"
#   like a console full of widgets...

import re
import shlex

from console import Console

global base
global console # Do I even want this?
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter

def init():
    global console
    from plugin import config_manager
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
    """Embedded Python console. use %help for a list of commands, and
    %help("help")
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
        """Print help text. Use '%help("command")' for more specific help.
        
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
            print(getattr(self, command).__doc__)
        else:
            print("Unknown command: %s" % (command, ) )

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
