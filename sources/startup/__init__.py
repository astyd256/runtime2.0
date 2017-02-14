
import __builtin__
import sys

from argparse import ArgumentParser


# settings

from .importers.settings import SettingsImporter

importer = SettingsImporter()
sys.meta_path.append(importer)
settings = __import__("settings")
sys.meta_path.remove(importer)


# override

from .override import override

parser = ArgumentParser(add_help=False)
parser.add_argument("-c", "--configure", dest="filename", default=None)

arguments, other = parser.parse_known_args()
if arguments.filename:
    override(arguments.filename)


# initialize

import utils.codecs
import utils.system
import utils.threads
import logs


# register libraries finder

from .importers.finder import ScriptingFinder

sys.meta_path.append(ScriptingFinder())


# start log server

from logs import VDOM_log_server

if settings.START_LOG_SERVER and settings.LOGGER == "native":
    VDOM_log_server().start()


# prepare manager

from importers.manager import ImportManager


# obsolete

from . import legacy
from .debug import debug, DebugFile

__builtin__.VDOM_CONFIG = legacy.VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = legacy.VDOM_CONFIG_1
__builtin__.system_options = {"server_license_type": "0", "firmware": "N/A", "card_state": "1", "object_amount": "15000"}
__builtin__.debug = debug
__builtin__.debugfile = DebugFile()
__builtin__._ = lambda value: value
