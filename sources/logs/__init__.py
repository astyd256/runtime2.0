
import sys

from .console import Console
from .sublogs import ServerLog, NetworkLog, SecurityLog


console = Console()

server_log = log = ServerLog()
network_log = NetworkLog()
security_log = SecurityLog()


from .logger import Logger
from .output import Output, ErrorOutput


logger = Logger()
logger.start()

sys.stdout = Output(sys.stdout)
sys.stderr = ErrorOutput(sys.stderr)


from .server import LogServer, VDOM_log_server
from .manager import LogManager, VDOM_log_manager


#   Audit
#       HTTP Requests
#       Logins in IDE & Admin Console
#   (Debug/Info/Error)
#   Server


# "ascii" if sys.stdout.encoding is None else sys.stdout.encoding


# from logging import log, network_log, security_log

# managers.log_manager.server_log
# managers.log_manager.network_log
# managers.log_manager.security_log
# managers.log_manager.application_log(...)

# managers.log_manager.logs.server
# managers.log_manager.logs.network
# managers.log_manager.logs.security
# managers.log_manager.logs.application(...)

# log.write("...", ...)
# log.write(warning="...", ...)
# log.write(error="...", ...)
