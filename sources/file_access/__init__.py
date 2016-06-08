
from .manager import FileManager, VDOM_file_manager
from .share import VDOM_share
from .daemon import FileWriter, VDOM_file_manager_writer

FILE = None
APPLICATION = application_xml = 0 # XML
TYPE = global_type = 1 # XML files of types: app/types
RESOURCE = resource = 3 # application's and type's resources: app/resources/<owner_id>
DATABASE = database = 5 # application's databases: app/databases/<owner_id>
MODULE = TYPE_SOURCE = type_source = 4 # runtime cache for Engine: app/objects
LIBRARY = 8 # application's libraries: app/lib/<id>
STORAGE = storage = 6 # application storage with base64'd filenames: app/storage/<id>
CACHE = cache = 2 # swap for source manager: app/applications/<id>/cache
# CERTIFICATE = certificate = 7 # server SSL certificates: app/cert
# LOG = 9 # log file: app/log
