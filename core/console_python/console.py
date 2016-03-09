from code import InteractiveInterpreter
import shlex
import sys
import re

from direct.showbase.DirectObject import DirectObject

from panda3d.lui import LUIRegion, LUIObject, LUIInputHandler, LUISprite, LUIVerticalLayout
from LUIScrollableRegion import LUIScrollableRegion
from LUIInputField import LUIInputField
from LUIFormattedLabel import LUIFormattedLabel

from plugin import configargs, get_config_value#, call_on_change

global base # This is just to suppress Eclipse error indicators

TEXT_MARGIN = (0.03, -0.06)
colors = {"font_color_banner": (1.0, 1.0, 0.0),
          "font_color_entry": (1.0, 1.0, 1.0),
          "font_color_entered": (0.8, 0.8, 0.8),
          "font_color_write": (0.0, 1.0, 0.0),
          "font_color_syntaxerror": (1.0, 0.0, 0.0),
          "font_color_traceback": (0.8, 0.0, 0.0),
          "font_color_stdout": (0.5, 0.5, 0.5),
          "font_color_stderr": (0.5, 0.0, 0.0),
          "font_color_weird": (1.0, 0.0, 1.0),
          "font_color_selected_history_item": (1.0, 1.0, 1.0)}

# Create and hide a Tk window, so that we can access the cut buffer
try:
    # Python2
    import Tkinter as tk
except ImportError:
    # Python3
    import tkinter as tk

# FIXME: Remember and put back the streams instead of using
# sys.__stdio__. In case of us already working in a stream-replacing
# environment.
class FakeIO:
    """A class to replace stdio in a with-statement."""
    def __init__(self):
        class PseudoStream:
            def __init__(self):
                self.data = ''
            def write(self, data):
                self.data += data
            def read(self):
                data = self.data
                self.data = ''
                return data
            
        self.fake_stdout = PseudoStream()
        self.fake_stderr = PseudoStream()
        
    def __enter__(self):
        sys.stdout = self.fake_stdout
        sys.stderr = self.fake_stderr
    
    def __exit__(self, type, value, traceback):
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        #print(type, value, traceback)

    def read_stdout(self):
        return self.fake_stdout.read()

    def read_stderr(self):
        return self.fake_stderr.read()


#   Frame                        # console_frame
#   + VerticalLayout             # console: This contains the history and the command line
#     | + ScrollableRegion       # history_region: This is the container for the history
#     |   + VerticalLayout       # history
#     |     + FormattedLabel     # These are the history items
#     |     + FormattedLabel
#     |     + FormattedLabel
#     |     + ...
#     + InputField               # command_line

class ConsoleGUI:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.history_objects = []
        
        self.console_frame = LUIObject()
        console = LUIVerticalLayout(parent = self.console_frame, spacing = 3)
        #console.use_dividers = True
        console.width = "100%"
        console.height = "100%"
        console.margin = 0
        
        self.history_region = LUIScrollableRegion()
        self.history_region.width = "100%"
        self.history_region.height = "100%"
        self.history_region.margin = 0
        console.add(self.history_region, "*")

        self.history = LUIVerticalLayout(parent = self.history_region.content_node,
                                         spacing = 2)
        self.history.width = "100%"
        #self.history.height = "100%"
        self.history.margin = 0

        self.command_line = LUIInputField()
        self.command_line.width = "100%"
        #self.command_line.height = "10%"
        console.add(self.command_line, "?")
        
        self.command_line.bind("tab", self.tab)
        self.command_line.bind("enter", self.enter)
        self.command_line.bind("control-c", self.copy)
        self.command_line.bind("control-v", self.paste)
        self.command_line.bind("control-x", self.cut)
        self.command_line.bind("control-u", self.kill_to_start)
        self.command_line.bind("control-k", self.kill_to_end)
        self.command_line.bind("control-l", self.kill_line)

    def set_visible(self, state):
        if state:
            self.console_frame.show()
            self.command_line.request_focus()
        else:
            self.console_frame.hide()
            # FIXME: Un-focus
        
    def write(self, text, color = "font_color_entry"):
        self.history_objects.append(ConsoleHistoryItem(self.history,
                                                       text,
                                                       color = color))
        self.history_region.scroll_to_bottom()

    def enter(self, event):
        print("text was entered. " + str(event))
        should_continue = self.interpreter.command(self.command_line.get_value()+"\n")
        if not should_continue:
            self.command_line.set_value("")

    def tab(self, event):
        # FIXME: Implement
        print("tab!")
        self.copy(event)

    def copy(self, event):
        # FIXME: If text is selected, limit to that.
        tk_window = tk.Tk()
        tk_window.withdraw()
        tk_window.clipboard_clear()
        tk_window.clipboard_append(self.command_line.get_value())
        print(tk_window, self.command_line.get_value(), tk_window.clipboard_get())
        tk_window.destroy()

    def cut(self, event):
        # FIXME: If text is selected, limit to that.
        self.copy(event)
        self.command_line.set_value("")

    def paste(self, event):
        # FIXME: Add text at cursor position.
        tk_window = tk.Tk()
        tk_window.withdraw()
        print(tk_window.clipboard_get())
        tk_window.destroy()

    def kill_to_start(self):
        # FIXME: Implement
        print("kill_to_start")

    def kill_to_end(self):
        # FIXME: Implement
        print("kill_to_end")

    def kill_line(self):
        # FIXME: Implement
        print("kill_line")

class ConsoleHistoryItem:
    def __init__(self, history, text, color = "font_color_entry"):
        self.history_entry = LUIFormattedLabel()
        self.history_entry.margin = (0, 0, 0, 0)
        #self.history_entry.height = "100%"
        #self.history_entry.width = "100%"
        history.add(self.history_entry, "?")
        self.history_entry.solid = True
        self.history_entry.bind("click", self.click)

        # FIXME: Choose color based on text_type
        for text_part in text.split("\n"):
            if text_part == "":
                self.history_entry.newline()
            else:
                self.history_entry.add(text_part, font_size = 15, color = colors[color])
                self.history_entry.newline()
        
        self.text = text
        self.original_color = color
        self.selected = False
        
    def click(self, lui_event):
        #print("click!")
        #print("  " + str(lui_event.name))        # click
        #print("  " + str(lui_event.sender))      # <lui.LUIObject object at 0x7f1a3eb66eb8>
        #print("  " + str(lui_event.coordinates)) # LPoint2f(58, 36)
        #print("  " + str(lui_event.message))     #
        self.selected = not self.selected
        if self.selected:
            self.history_entry.color = colors["font_color_selected_history_item"]
            print(colors["font_color_selected_history_item"])
        else:
            self.history_entry.color = colors[self.original_color]
            print(colors[self.original_color])


class BufferingInterpreter(InteractiveInterpreter):
    def __init__(self, flush_sink, **kwargs):
        InteractiveInterpreter.__init__(self, **kwargs)
        self.write_sink = []
        self.flush_queue = []
        self.flush_sink = flush_sink
        self.mode = None
    
    def set_write_mode(self, mode):
        if mode == self.mode:
            pass
        else:
            self.flush_write_sink()
            self.mode = mode
    
    def flush_write_sink(self):
        if self.write_sink != []:
            self.flush_queue.append((self.mode, "".join(self.write_sink)))
            self.write_sink = []
    
    def flush(self):
        if len(self.write_sink) > 0:
            self.flush_write_sink()
        for (mode, data) in self.flush_queue:
            self.flush_sink(mode, data)
        self.flush_queue = []
    
    def write(self, data):
        if data != '':
            self.write_sink.append(data)
    
    def showsyntaxerror(self, filename=None):
        self.set_write_mode('font_color_syntaxerror')
        InteractiveInterpreter.showsyntaxerror(self, filename=filename)
    
    def showtraceback(self):
        self.set_write_mode('font_color_traceback')
        InteractiveInterpreter.showtraceback(self)

class Console(DirectObject, BufferingInterpreter):
    """An interactive Python interpreter, and the DirectGUI elements
    surrounding it."""
    def __init__(self, interpreter_locals = {}):
        DirectObject.__init__(self)
        self.gui_window = ConsoleGUI(self)
        BufferingInterpreter.__init__(self, lambda mode, data: self.gui_window.write(data, mode), locals = interpreter_locals)
        self.window = base.win
        self.visible = False
        self.gui_window.set_visible(self.visible)

        self.fake_io = FakeIO()
        self.color_stack = False

        lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec rhoncus velit sit amet dolor auctor consequat. Donec pretium lectus sed tortor pharetra tristique. Aliquam vel pharetra ligula. Sed eget neque quis velit imperdiet molestie. Cras a sapien vitae ligula maximus tincidunt. Aenean sit amet felis velit. Fusce consectetur ante lacinia nunc varius tristique. Pellentesque sollicitudin vehicula dictum. Nulla auctor erat placerat blandit molestie. Donec quam enim, vestibulum at elit id, elementum vestibulum nulla. In nec efficitur magna. Morbi facilisis ante non nulla fermentum, quis commodo mauris elementum. Pellentesque rutrum tellus purus, quis posuere velit tincidunt in."
        if 'console_command' in interpreter_locals.keys():
            banner = interpreter_locals['console_command'].__doc__
        else:
            banner = "Python console. Have fun!"
        self.set_write_mode("font_color_banner")
        self.write(banner)
        self.flush()

    def destroy(self):
        self.gui_window.destroy()
        self.fake_io = None

    # Python Interpreter-relevant methods

    def command(self, input_text):
        self.color_stack = None
        if input_text != '':
            self.set_write_mode("font_color_entered")
            self.write(input_text)
            if input_text.startswith('%'):
                # Apply console magic
                space_pos = input_text.find(" ")
                if space_pos != -1:
                    func = input_text[1:space_pos]
                    arg = input_text[space_pos+1:-1]
                else:
                    func = input_text[1:-1]
                    arg = ""
                input_text = 'console_command.%s(%s)' % (func, repr(arg))
                #print(repr(input_text))
            try:
                self.set_write_mode("font_color_weird")
                with self.fake_io:
                    should_continue = self.runsource(input_text)
                self.set_write_mode("font_color_stdout")
                self.write(self.fake_io.read_stdout())
                self.set_write_mode("font_color_stderr")
                self.write(self.fake_io.read_stderr())
                if should_continue:
                    self.set_write_mode("font_color_weird")
                    self.write("Input was incomplete.")
                self.flush()
                return should_continue
            except Exception as e:
                print("EXCEPTION!!!")
                print(repr(e))
        else:
            return True

# Console magic

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
    def __init__(self, plugin_manager, config_manager, command_prefix = "%", max_command_length = None):
        self.plugin_manager = plugin_manager
        self.config_manager = config_manager
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
        
        loaded = self.plugin_manager.get_loaded_plugins()
        active = self.plugin_manager.get_active_plugins()
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
            for section in self.config_manager.sections():
                print(section)
        elif len(args) == 1:
            for item, value in self.config_manager.items(args[0]):
                print(str(item) + " = " + str(value))
        elif len(args) == 2:
            print(self.config_manager.get(args[0], args[1]))

    @tokenize_magic()
    def cfgset(self, section, variable, value):
        """Set a configuration variable.
        
        Usage: %cfgset section variable value
        """
        self.config_manager.set(section, variable, value)
    
    @tokenize_magic()
    def cfgwrite(self):
        """Write changes back to config file.
        
        Write changed configuration values into the file that has
        been determined to be the appropriate one by virtue of
        being the last one in the list of config files that actually
        exists."""
        self.config_manager.write()

    @tokenize_magic()
    def plhelp(self, plugin_name):
        """Show docstring for plugin.
        
        Usage: %plhelp plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # can't be found.
        print(self.plugin_manager.plugins[plugin_name].__doc__)

    @tokenize_magic()
    def plload(self, plugin_name):
        """Load and initialize a plugin.
        
        Usage: %plload plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # can't be found or inited.
        # FIXME: Also, how about a just-load option?
        self.plugin_manager.load_plugin(plugin_name)
        self.plugin_manager.init_plugin(plugin_name)

    @tokenize_magic()
    def plreload(self, plugin_name):
        """Unload, load and initialize a plugin.
        
        Usage: %plreload plugin_name"""
        self.plugin_manager.reload_plugin(plugin_name)
        self.plugin_manager.init_plugin(plugin_name)

    @tokenize_magic()
    def plunload(self, plugin_name):
        """Destroy and unload a plugin.
        
        Usage: %plunload plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # isn't active, or even loaded.
        self.plugin_manager.unload_plugin(plugin_name)

    @tokenize_magic()
    def plinit(self, plugin_name):
        """Initialize a loaded but inactive plugin.
        
        Usage: %plinit plugin_name"""
        # FIXME: There should be logic here, in case that the plugin
        # can't be inited. Maybe there should also be a check whether
        # it is even loaded in the first place, or already active?
        self.plugin_manager.load_plugin(plugin_name)
        self.plugin_manager.init_plugin(plugin_name)
