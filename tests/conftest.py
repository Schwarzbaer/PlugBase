import pytest

from src.config_manager import ConfigManager
from src.plugin_manager import PluginManager

@pytest.fixture
def config_manager():
    return ConfigManager()

@pytest.fixture
def plugin_manager(config_manager):
    return PluginManager(config_manager=config_manager)
