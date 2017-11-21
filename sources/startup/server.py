
import sys
from socket import socket
from argparse import ArgumentParser
import settings
from utils.verificators import port, uuid
from .legacy import VDOM_CONFIG


# verify that server is not running

probe_socket = socket()
try:
    probe_socket.bind((settings.SERVER_ADDRESS, settings.SERVER_PORT))
except:
    sys.stdout.write("Server is already running or incorrect address or port\n")
    sys.exit(0)
finally:
    probe_socket.close()

# parsing command line arguments

parser = ArgumentParser(prog="server")

parser.add_argument("-l", "--listen", type=port, metavar="address", help="Override server listening address")
parser.add_argument("-p", "--port", type=port, metavar="port", help="Override server listening port")
parser.add_argument("-a", "-d", "--application", "--default", type=uuid, metavar="identifier", help="Application to start")
parser.add_argument("-c", "--configure", metavar="filename", help="Load configuration from the file")
parser.add_argument("--preload", action='store_true', help="Preload default application",)
parser.add_argument("--profile", action='store_true', help="Enable profiling",)

arguments = parser.parse_args()


if arguments.listen:
    VDOM_CONFIG["SERVER-ADDRESS"] = settings.SERVER_ADDRESS = arguments.listen

if arguments.port:
    VDOM_CONFIG["SERVER-PORT"] = settings.SERVER_PORT = arguments.port

if arguments.application:
    settings.DEFAULT_APPLICATION = arguments.application

if arguments.preload:
    settings.PRELOAD_DEFAULT_APPLICATION = True

if arguments.profile:
    settings.PROFILING = True
