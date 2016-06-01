
import actions
from utils.autoparse import AutoArgumentParser


parser = AutoArgumentParser(prog="manage", module=actions, alias="action", default=actions.shell.run)
arguments = parser.parse_args()
