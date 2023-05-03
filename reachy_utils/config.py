from functools import partial
import yaml
import os


config_file = os.path.expanduser("~/.reachy.yaml")


def get_reachy_config():
    try:
        with open(config_file) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
            return config
    except FileNotFoundError:
        print(f"Config file {config_file} not found.")
        exit(-1)


def _get_config_parameter(parameter: str, part=None):
    config = get_reachy_config()
    try:
        return config[parameter]
    except KeyError:
        print(f"{parameter} not found in {config_file}")
        return -1


get_reachy_generation = partial(_get_config_parameter, "generation")
get_reachy_model = partial(_get_config_parameter, "model")
get_zuuu_version = partial(_get_config_parameter, "zuuu_model")
get_camera_parameters = partial(_get_config_parameter, "camera_parameters")
get_reachy_serial_number = partial(_get_config_parameter, "serial_number")