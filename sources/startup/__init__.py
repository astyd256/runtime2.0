
import __builtin__
import sys


# settings

from .importing import VDOM_settings_importer

sys.meta_path.append(VDOM_settings_importer())
settings = __import__("settings")


# initialize

import utils.codecs
import utils.system
import utils.threads
import logs


# include modules to search

sys.path.append(settings.MODULES_LOCATION)


# register metaimporter

from .metaimporter import VDOM_metaimporter
sys.meta_path.append(VDOM_metaimporter())


# start log server

from logs import VDOM_log_server

if settings.START_LOG_SERVER:
    VDOM_log_server().start()


# obsolete

from .debug import debug, DebugFile

__builtin__.VDOM_CONFIG = settings.VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = settings.VDOM_CONFIG_1
__builtin__.system_options = {"server_license_type": "0", "firmware": "N/A", "card_state": "0", "object_amount": "0"}
__builtin__.debug = debug
__builtin__.debugfile = DebugFile()
__builtin__._ = lambda value: value
