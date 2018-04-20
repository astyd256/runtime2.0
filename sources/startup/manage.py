
import actions
from utils.autoparse import AutoArgumentParser

parser = AutoArgumentParser(prog="manage", module=actions, alias="action", default=actions.shell.run)
parser.add_argument("-c", "--configure", metavar="filename", help="Load configuration from the file")

arguments = parser.parse_args()
