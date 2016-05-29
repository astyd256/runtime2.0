
import sys
from socket import socket
from argparse import ArgumentParser
import settings
from utils.verificators import port


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

parser.add_argument("-l", "--listen", type=port, help="Override server listening address")
parser.add_argument("-p", "--port", type=port, help="Override server listening port")
parser.add_argument("-a", "--application", help="Application to start")
parser.add_argument("-c", "--configure", help="Load configuration from the file")

arguments = parser.parse_args()


if arguments.listen:
    settings.VDOM_CONFIG["SERVER-ADDRESS"] = settings.SERVER_ADDRESS = arguments.listen

if arguments.port:
    settings.VDOM_CONFIG["SERVER-PORT"] = settings.SERVER_PORT = arguments.port

if arguments.application:
    settings.DEFAULT_APPLICATION = arguments.application

if arguments.configure:
    raise NotImplementedError
