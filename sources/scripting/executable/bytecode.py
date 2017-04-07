
import marshal
import json

import settings
import managers
import file_access

from logs import server_log
from utils.properties import aroproperty, roproperty
from .constants import LISTING, SYMBOLS, BYTECODE


class Bytecode(object):

    __slots__ = "_bytecode", "_symbols"

    source_extension = aroproperty()
    extensions = aroproperty()

    @classmethod
    def cleanup(cls, executable):
        if settings.STORE_BYTECODE:
            for entity, extension in cls.extensions.iteritems():
                if extension:
                    location = executable.locate(entity)
                    if location:
                        managers.file_manager.delete(file_access.FILE, None, location + extension)

    @classmethod
    def compile(cls, executable):
        raise NotImplementedError

    @classmethod
    def restore(cls, executable):
        bytecode, symbols = None, None

        if settings.STORE_BYTECODE:
            extension = cls.extensions.get(BYTECODE)
            if extension:
                location = executable.locate(BYTECODE)
                if location:
                    bytecode = managers.file_manager.read(file_access.FILE, None, location + extension, default=None)
                    if bytecode:
                        bytecode = marshal.loads(bytecode)

                        extension = cls.extensions.get(SYMBOLS)
                        if extension:
                            location = executable.locate(SYMBOLS)
                            if location:
                                symbols = managers.file_manager.read(file_access.FILE, None, location + extension, default=None)
                                if symbols:
                                    symbols = json.loads(symbols)

        if bytecode:
            return cls(executable, bytecode, listing=None, symbols=symbols, store=False)
        else:
            return None

    def __init__(self, executable, bytecode, listing=None, symbols=None, store=True):
        self._bytecode = bytecode
        self._symbols = symbols

        if store and settings.STORE_BYTECODE:
            extension = self.extensions.get(BYTECODE)
            if extension:
                location = executable.locate(BYTECODE)
                if location:
                    managers.file_manager.write(file_access.FILE, None, location + extension, marshal.dumps(bytecode))

            if listing:
                extension = self.extensions.get(LISTING)
                if extension:
                    location = executable.locate(LISTING)
                    if location:
                        managers.file_manager.write(file_access.FILE, None, location + extension, listing)

            if symbols:
                extension = self.extensions.get(SYMBOLS)
                if extension:
                    location = executable.locate(LISTING)
                    if location:
                        managers.file_manager.write(file_access.FILE, None, location + extension, json.dumps(symbols))

    bytecode = roproperty("_bytecode")
    symbols = roproperty("_symbols")

    def explain(self):
        pass

    def execute(self, context, namespace, arguments):
        raise NotImplementedError


class ErrorBytecode(Bytecode):

    __slots__ = ("_message", "_details")

    source_extension = ()
    extensions = {}

    message = roproperty("_message")
    details = roproperty("_details")

    def __init__(self, message, details):
        self._message = message
        self._details = details

    def explain(self):
        server_log.error(self._details)

    def execute(self, context, namespace, arguments):
        server_log.error(self._details)
        raise Exception(self._message)
