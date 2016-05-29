
import actions
from utils.autoparse import AutoArgumentParser


parser = AutoArgumentParser(prog="manage", module=actions, alias="action")
arguments = parser.parse_args()
