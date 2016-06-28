
from .manager import FileManager, VDOM_file_manager
from .share import VDOM_share
from .daemon import FileWriter, VDOM_file_manager_writer


FILE = None

APPLICATION = application_xml = 0
TYPE = global_type = 1

CACHE = cache = 2

RESOURCE = resource = 3

MODULE = TYPE_SOURCE = type_source = 4
LIBRARY = 8

DATABASE = database = 5
STORAGE = storage = 6

# CERTIFICATE = certificate = 7
# LOG = 9
