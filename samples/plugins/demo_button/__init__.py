dependencies = ["demo_smiley"]
implements = "demo_button"

from direct.gui.DirectGui import DirectButton

from plugin import get_config_value, set_config_value

global base
global plugin_manager # Set by the plugin_manager, used from within the InteractiveInterpreter

global button

def build():
    global button
    button = DirectButton(parent = base.aspect2d,
                          frameSize = (base.a2dRight,
                                       base.a2dRight * 0.5,
                                       base.a2dBottom,
                                       base.a2dBottom * 0.5),
                          command = click,
                          )

def destroy():
    pass

def click():
    rot_speed = get_config_value("demo_smiley", "rotation_speed", float)
    rot_speed *= 2.0
    print(rot_speed)
    set_config_value("demo_smiley", "rotation_speed", rot_speed)
    