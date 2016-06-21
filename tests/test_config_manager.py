import pytest

from src.config_manager import FRAMEWORK_CONFIG


def test_type_inference(config_manager):
    assert isinstance(config_manager.get("types", "var_str"), str)
    assert isinstance(config_manager.get("types", "var_int"), int)
    assert isinstance(config_manager.get("types", "var_float"), float)
    assert isinstance(config_manager.get("types", "var_bool"), bool)
    assert isinstance(config_manager.get("types", "var_tuple"), tuple)
    assert isinstance(config_manager.get("types", "var_list"), list)
    assert isinstance(config_manager.get("types", "var_dict"), dict)

def test_hierarchy(config_manager):
    assert config_manager.get("hierarchy", "var_a") == 1
    assert config_manager.get("hierarchy", "var_a", level=FRAMEWORK_CONFIG) == 0
