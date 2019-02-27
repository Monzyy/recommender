import json
import sys

settings = {}

this_module = sys.modules[__name__]
this_module.settings = {}


def set_settings(config):
    with open('config.json', 'r') as f:
        this_module.settings = json.load(f)[config]
