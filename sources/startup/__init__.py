
import __builtin__
import sys

from argparse import ArgumentParser


# python: http://bugs.python.org/issue7980

import datetime
datetime.datetime.strptime("2012-01-01", "%Y-%m-%d")


#Hotfix to allow urllib certificate validation
try:
    import os, ssl, certifi
    def new_ssl_context_decorator(*args, **kwargs):
        kwargs['cafile'] = certifi.where()
        return ssl.create_default_context(*args, **kwargs)
    ssl._create_default_https_context = new_ssl_context_decorator
except ImportError:
    print("Unable to set default ssl validation context for urllib. Check certifi library presence")

# settings

from .importers.settings import SettingsImporter  # noqa

importer = SettingsImporter()
sys.meta_path.append(importer)
settings = __import__("settings")
sys.meta_path.remove(importer)


# override

from .override import override  # noqa

parser = ArgumentParser(add_help=False)
parser.add_argument("-c", "--configure", dest="filename", default=None)

arguments, other = parser.parse_known_args()
if arguments.filename:
    override(arguments.filename)


# hack to run builder cleanly

if settings.MANAGE:
    from . import builder  # noqa


# initialize

import utils.codecs  # noqa
import utils.system  # noqa
import utils.threads  # noqa
import logs  # noqa


# register libraries finder

from .importers.finder import ScriptingFinder  # noqa

sys.meta_path.append(ScriptingFinder())


# start log server

from logs import VDOM_log_server  # noqa

if settings.START_LOG_SERVER and settings.LOGGER == "native":
    VDOM_log_server().start()


# prepare manager

from importers.manager import ImportManager  # noqa


# obsolete

from . import legacy  # noqa
from .debug import debug, DebugFile  # noqa

__builtin__.VDOM_CONFIG = legacy.VDOM_CONFIG
__builtin__.VDOM_CONFIG_1 = legacy.VDOM_CONFIG_1
__builtin__.system_options = {"server_license_type": "0", "firmware": "N/A", "card_state": "1", "object_amount": "15000"}
__builtin__.debug = debug
__builtin__.debugfile = DebugFile()
__builtin__._ = lambda value: value
