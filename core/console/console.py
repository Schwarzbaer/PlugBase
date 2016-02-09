from code import InteractiveInterpreter
import shlex
import sys

from direct.showbase.DirectObject import DirectObject

from panda3d.lui import LUIRegion, LUIObject, LUIInputHandler, LUISprite, LUIVerticalLayout
from LUISkin import LUIDefaultSkin
from LUIFrame import LUIFrame
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
#     + InputField

class ConsoleGUI:
    def __init__(self, interpreter):
        self.interpreter = interpreter
        self.history_objects = []
        
        skin = LUIDefaultSkin()
        skin.load()

        region = LUIRegion.make("LUI", base.win)
        handler = LUIInputHandler()
        base.mouseWatcher.attach_new_node(handler)
        region.set_input_handler(handler)

        self.console_frame = LUIFrame(parent = region.root,
                                      pos = (0, 0),
                                      width = base.win.get_x_size() - 10,
                                      height = base.win.get_y_size() * 0.75,
                                      style = LUIFrame.FS_raised,
                                      #style = LUIFrame.FS_sunken,
                                      margin = (5, 5, 5, 5),
                                      )
        console = LUIVerticalLayout(parent = self.console_frame, spacing = 3)
        #console.use_dividers = True
        console.margin = (0, 0, 0, 0)
        console.width = self.console_frame.width
        
        self.history_region = LUIScrollableRegion(margin = 0, width = console.width - 10)
        console.add(self.history_region)
        self.history = LUIVerticalLayout(parent = self.history_region.content_node,
                                         spacing = 2)
        self.history.margin = (0, 0, 0, 0)
        self.history.width = self.history_region.width

        self.command_line = LUIInputField(width = console.width - 10)
        console.add(self.command_line)
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
        #self.history_region.scroll_to_bottom()

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
        self.history_entry = LUIFormattedLabel(margin = (0, 0, 0, 0),
                                               #padding = 10,
                                               #color=(0.4,0.0,0.0, 1.0),
                                               )
        history.add(self.history_entry)
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
        self.accept("toggle_console", self.toggle_visibility)
        #self.accept("window-event", self.window_event)

        self.fake_io = FakeIO()
        self.history = []
        self.color_stack = False

        lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec rhoncus velit sit amet dolor auctor consequat. Donec pretium lectus sed tortor pharetra tristique. Aliquam vel pharetra ligula. Sed eget neque quis velit imperdiet molestie. Cras a sapien vitae ligula maximus tincidunt. Aenean sit amet felis velit. Fusce consectetur ante lacinia nunc varius tristique. Pellentesque sollicitudin vehicula dictum. Nulla auctor erat placerat blandit molestie. Donec quam enim, vestibulum at elit id, elementum vestibulum nulla. In nec efficitur magna. Morbi facilisis ante non nulla fermentum, quis commodo mauris elementum. Pellentesque rutrum tellus purus, quis posuere velit tincidunt in."
        if 'console_command' in interpreter_locals.keys():
            banner = interpreter_locals['console_command'].__doc__
        else:
            banner = "Python console. Have fun!"
        self.set_write_mode("font_color_banner")
        self.write(banner)
        self.flush()

    # Python Interpreter-relevant methods

    def command(self, input_text):
        self.color_stack = None
        if input_text != '':
            self.set_write_mode("font_color_entered")
            self.write(input_text)
            if input_text[0] == '%':
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

    # Things related to the plugin's general functionality.

    def toggle_visibility(self):
        if self.visible:
            # Hide Console
            self.visible = False
        else:
            # Show console
            #self.update_gui()
            self.visible = True
        self.gui_window.set_visible(self.visible)
    
    def destroy(self):
        # FIXME: delete all the nodes / nodepaths and forget about all events
        pass
