dependencies = ["inexistant_plugin"]
implements = "nothing"
extends = []

def build(plugin_manager):
    print("This should never appear; impossible plugin was initialized!")
