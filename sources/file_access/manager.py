
import io
import os
import shutil

from collections import deque
from threading import RLock
from tempfile import NamedTemporaryFile # _TemporaryFileWrapper

import settings
import file_access

from utils.system import *
from utils.mutex import VDOM_named_mutex
from utils.tracing import format_exception_trace
# from utils.file_argument import Attachment

from .auxiliary import cleanup_directory
from .daemon import FileWriter


# application_path = "applications"
# global_types_path = "types"
# type_source_path = "objects"
# py_files_cache = "cache"
# resources_path = "resources"
# application_file_name = "application.xml"
# databases_path = "databases"


class FileManager(object):

    def __init__(self):
        self._lock = RLock()
        self._queue = deque()
        self._daemon = None

    # threading

    def start_daemon(self):
        if self._daemon is None:
            self._daemon = FileWriter(self)
            self._daemon.start()
        return self._daemon

    def work(self):
        with self._lock:
            queries = tuple(self._queue)
            self._queue.clear()
        for arguments in queries:
            try:
                self.write(*arguments)
            except:
                log.error("Unable to save %s, details below\n%s" %
                    (self.locate(arguments[:3]), format_exception_trace(locals=True, separate=True)))

    # locations

    def locate(self, category=None, owner=None, name=None, *arguments):
        if category is None:
            segments = (owner, name) + arguments
        elif category == file_access.APPLICATION:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / application_path="applications" / application_id / application_file_name="app.xml"
            segments = (settings.APPLICATIONS_LOCATION, owner, name) + arguments
        elif category == file_access.TYPE:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / global_types_path="types" / object_name
            segments = (settings.TYPES_LOCATION, owner, name) + arguments
        elif category == file_access.RESOURCE:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / resources_path="resources" / owner_id / object_name
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / resources_path="resources"
            segments = settings.RESOURCES_LOCATION, owner, name
        elif category == file_access.DATABASE:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / databases_path="databases" / owner / object_name
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / databases_path="databases"
            segments = settings.DATABASES_LOCATION, owner, name
        elif category == file_access.MODULE:
            assert owner is not None
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / type_source_path="objects" / object_name
            # segments = settings.MODULES_LOCATION, name
            segments = settings.TYPES_LOCATION, owner, name
        elif category == file_access.LIBRARY:
            assert owner is not None
            assert not arguments
            # segments = settings.LIBRARIES_LOCATION, owner, name
            segments = settings.APPLICATIONS_LOCATION, owner, settings.APPLICATION_LIBRARIES_DIRECTORY, name
        elif category == file_access.STORAGE:
            # VDOM_CONFIG["FILE-STORAGE-DIRECTORY"] / application_id / file_name
            # VDOM_CONFIG["FILE-STORAGE-DIRECTORY"] / application_id
            segments = settings.STORAGE_LOCATION, owner, name
        elif category == file_access.CACHE:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / application_path="applications" / application_id / py_files_cache="cache" / object_name
            segments = settings.CACHE_LOCATION, owner, name
        elif category == file_access.CERTIFICATE:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / certificates="cert" / file_name
            assert owner is None
            segments = settings.CERTIFICATES_LOCATION, name
        elif category == file_access.LOG:
            # VDOM_CONFIG["FILE-ACCESS-DIRECTORY"] / certificates="cert" / file_name
            assert owner is None
            segments = settings.LOGS_LOCATION, name
        else:
            raise Exception("Unknown category: %r" % category)
        return os.path.join(*filter(None, segments))

    def ensure(self, category, owner, mode, name=None):
        if "w" not in mode:
            return
        if category in (file_access.RESOURCE, file_access.DATABASE, file_access.STORAGE, file_access.CACHE):
            location = self.locate(category, owner)
            if not os.path.isdir(location):
                try:
                    os.makedirs(location)
                except Exception as error:
                    print "Ensure %s directory error: %s" % (location, error)

    # elementary

    def list(self, category=None, owner=None, name=None):
        location = self.locate(category, owner, name)
        try:
            return os.listdir(location)
        except:
            print "List storage %s directory error: %s" % (location, error)

    def exists(self, category, owner=None, name=None):
        location = self.locate(category, owner, name)
        return os.path.exists(location)

    def open(self, category, owner, name=None, mode="r", buffering=-1, encoding=None, errors=None, newline=""):
        location = self.locate(category, owner, name)
        # self.ensure(category, owner, mode)
        return io.open(location, mode, buffering, encoding, errors, None if "b" in mode else newline)

    def open_temporary(self, category, owner, mode="w+b", buffering=-1, encoding=None, suffix="", prefix=""):
        if category is not None:
            raise Exception("Unable to create temporary non-file resource")
        if encoding is not None:
            raise Exception("Unable to create temporary file with encoding")
        return NamedTemporaryFile(mode=mode, buffering=buffering, suffix=suffix, prefix=prefix,
            dir=os.path.abspath(settings.TEMPORARY_LOCATION))

    def size(self, category, owner, name):
        try:
            return os.path.getsize(self.locate(category, owner, name))
        except os.error:
            return None

    def read(self, category, owner, name, encoding=None):
        location = self.locate(category, owner, name)
        mode = "r" if encoding else "rb"
        with io.open(location, mode, encoding=encoding, newline=None if "b" in mode else "") as file:
            return file.read()

    # There are some code pieces from write

    # TODO: This dirty hack must be checked for new UWSGI layer
    # if isinstance(content, Attachment):
    #     if content._get_realpath():
    #         if not content.handler.closed:
    #             content.handler.close()
    #         try:
    #             os.rename(content._get_realpath(), location)
    #         except OSError:
    #             os.remove(location)
    #             os.rename(content._get_realpath(), location)
    #         content._del_fileobj()
    #         return
    #     else:
    #         content = content.handler
    #         async = False

    # TODO: This dirty hack possible not work on 2.7.11 or later
    # elif isinstance(content, _TemporaryFileWrapper):
    #     if not content.closed: # .closed -> .close_called ???
    #         content.close() # on os.name == "nt" no .close in object
    #     try:
    #         os.rename(content.name, location)
    #     except OSError:
    #         os.remove(location)
    #         os.rename(content.name, location)
    #     return

    def write(self, category, owner, name, content, encoding=None, async=False, safely=False):
        if async:
            with self._lock:
                self._queue.append((category, owner, name, content, encoding, False, safely))
                if self._daemon is None:
                    self.start_daemon()
        else:
            location = self.locate(category, owner, name)
            mode = "w" if encoding else "wb"
            # self.ensure(category, owner, mode)
            with VDOM_named_mutex(location):
                if safely:
                    proper_location, location = location, location + ".temporary"
                with io.open(location, mode, encoding=encoding, newline=None if "b" in mode else "") as file:
                    if hasattr(content, "read"):
                        shutil.copyfileobj(content, file)
                    else:
                        file.write(content)
                if safely:
                    shutil.move(location, proper_location)

    def delete(self, category, owner, name):
        location = self.locate(category, owner, name)
        with VDOM_named_mutex(location):
            try:
                os.remove(location)
            except Exception as error:
                print "Delete %s file error: %s" % (location, error)

    # directories

    def prepare_directory(self, category, owner, cleanup=True):
        location = self.locate(category, owner)
        try:
            if os.path.isdir(location):
                if cleanup:
                    cleanup_directory(location, ignore_errors=True)
            else:
                os.makedirs(location)
        except Exception as error:
            print "Prepare %s directory error: %s" % (location, error)

    def cleanup_directory(self, category, owner, remove=False):
        location = self.locate(category, owner)
        try:
            if os.path.isdir(location):
                cleanup_directory(location, ignore_errors=True, remove=remove)
            elif os.path.exists(location):
                raise Exception("Unable to cleanup non-directory: %s" % location)
        except Exception as error:
            print "Cleanup %s directory error: %s" % (location, error)

    # storage

    def create_storage_directory(self, owner, folder_name):
        location = self.locate(file_access.STORAGE, owner, folder_name)
        try:
            os.makedirs(location)
        except Exception as error:
            print "Create storage %s directory error: %s" % (location, error)

    def list_storage_directory(self, owner, folder_name):
        location = self.locate(file_access.STORAGE, owner, folder_name)
        try:
            return os.listdir(location)
        except:
            print "List storage %s directory error: %s" % (location, error)

    def delete_storage_directory(self, owner, folder_name):
        location = self.locate(file_access.STORAGE, owner, folder_name)
        try:
            shutil.rmtree(location)
        except:
            print "Delete storage %s directory error: %s" % (location, error)

    # libraries

    def write_library(self, owner, name, data):
        # fname = os.path.join(VDOM_CONFIG["LIB-DIRECTORY"], appid, libname + ".py")
        self.write(file_access.LIBRARY, owner, name, data, encoding="utf-8")

    def delete_library(self, owner, name):
        # fname = os.path.join(VDOM_CONFIG["LIB-DIRECTORY"], appid, libname + ".py")
        # self.cleanup_directory(file_access.LIBRARY, owner)
        self.delete(file_access.LIBRARY, owner, name)
        # try:
        #     os.remove(fname)
        # except:
        #     pass
        # try:
        #     os.remove(fname + "c")
        # except:
        #     pass


VDOM_file_manager = FileManager
