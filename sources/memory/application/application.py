

import sys
import base64

from threading import RLock
from collections import defaultdict
from cStringIO import StringIO

import settings
import managers
import file_access

from logs import log
from database.dbobject import VDOM_sql_query
from utils.properties import constant, roproperty, rwproperty

from .. import PYTHON_LANGUAGE, VSCRIPT_LANGUAGE, PYTHON_EXTENSION, VSCRIPT_EXTENSION, \
    APPLICATION_START_CONTEXT, SESSION_START_CONTEXT, REQUEST_START_CONTEXT
from ..generic import MemoryBase
from .objects import MemoryObjects
from .events import MemoryEvents
from .actions import MemoryActions
from .bindings import MemoryBindings


NOT_LOADED = "NOT LOADED"


class MemoryApplicationSketch(MemoryBase):

    is_application = constant(True)
    is_object = constant(False)

    generic = APPLICATION_START_CONTEXT, SESSION_START_CONTEXT, REQUEST_START_CONTEXT

    def get_library_executable(self, name):
        from scripting.executable import select_library_class
        return select_library_class(self._scripting_language)(self, name)

    @property
    def scripting_extension(self):
        if self._scripting_language == PYTHON_LANGUAGE:
            return PYTHON_EXTENSION
        elif self._scripting_language == VSCRIPT_LANGUAGE:
            return VSCRIPT_EXTENSION
        else:
            return ""

    def __init__(self, callback):
        self._callback = callback
        self._lock = RLock()
        self._save_queue = False

        self._id = None
        self._name = None
        self._description = u""
        self._version = u"1"
        self._owner = u""
        self._password = u""
        self._active = 1
        self._index = u""
        self._icon = u""
        self._server_version = u""
        self._scripting_language = u"vscript"
        self._default_language = u"en-US"
        self._current_language = u"en-US"

        self._objects = MemoryObjects(self)
        self._events = MemoryEvents(self)
        self._actions = MemoryActions(self)

        self._libraries = {}
        self._sentences = {}
        self._bindings = MemoryBindings(self)

    lock = roproperty("_lock")
    application = property(lambda self: self)
    changes = roproperty("_changes")
    is_virtual = virtual = constant(False)

    id = rwproperty("_id")
    name = rwproperty("_name")
    description = rwproperty("_description")
    version = rwproperty("_version")
    owner = rwproperty("_owner")
    password = rwproperty("_password")
    active = rwproperty("_active")
    index = rwproperty("_index")
    icon = rwproperty("_icon")
    server_version = rwproperty("_server_version")
    scripting_language = rwproperty("_scripting_language")
    default_language = rwproperty("_default_language")
    current_language = rwproperty("_current_language")

    objects = roproperty("_objects")
    events = roproperty("_events")
    actions = roproperty("_actions")

    libraries = roproperty("_libraries")
    sentence = roproperty("_sentences")
    bindings = roproperty("_bindings")

    def __invert__(self):
        if self._id is None:
            raise Exception(u"Application require identifier")
        if self._name is None:
            raise Exception(u"Application require name")

        self.__class__ = MemoryApplication
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, (
            "application",
            ":".join(filter(None, (getattr(self, "_id", None), getattr(self, "_name", "").lower()))),
            "sketch")))


class MemoryApplication(MemoryApplicationSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new application")

    id = roproperty("_id")
    name = rwproperty("_name", notify="autosave")
    description = rwproperty("_description", notify="autosave")
    version = rwproperty("_version", notify="autosave")
    owner = rwproperty("_owner", notify="autosave")
    password = rwproperty("_password", notify="autosave")
    active = rwproperty("_active", notify="autosave")
    index = rwproperty("_index", notify="autosave")
    icon = rwproperty("_icon", notify="autosave")
    server_version = rwproperty("_server_version", notify="autosave")
    scripting_language = rwproperty("_scripting_language", notify="autosave")
    default_language = rwproperty("_default_language", notify="autosave")
    current_language = rwproperty("_current_language", notify="autosave")

    # unsafe
    def compose(self, file=None, shorter=False):
        if not file:
            file = StringIO()
            self.compose(file=file, shorter=True)
            return file.getvalue()

        file.write(u"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        file.write(u"<Application>\n")

        file.write(u"\t<Information>\n")
        file.write(u"\t\t<ID>%s</ID>\n" % self._id)
        file.write(u"\t\t<Name>%s</Name>\n" % self._name.encode("xml"))
        if self._description:
            file.write(u"\t\t<Description>%s</Description>\n" % self._description.encode("xml"))
        file.write(u"\t\t<Version>%s</Version>\n" % self._version.encode("xml"))
        if self._owner:
            file.write(u"\t\t<Owner>%s</Owner>\n" % self._owner.encode("xml"))
        if self._password:
            file.write(u"\t\t<Password>%s</Password>\n" % self._password.encode("xml"))
        file.write(u"\t\t<Active>%d</Active>\n" % self._active)
        if self._index:
            file.write(u"\t\t<Index>%s</Index>\n" % self._index)
        if self._icon:
            file.write(u"\t\t<Icon>%s</Icon>\n" % self._icon)
        if self._server_version:
            file.write(u"\t\t<ServerVersion>%s</ServerVersion>\n" % self._server_version)
        if self._scripting_language:
            file.write(u"\t\t<ScriptingLanguage>%s</ScriptingLanguage>\n" % self._scripting_language)
        if self._default_language:
            file.write(u"\t\t<DefaultLanguage>%s</DefaultLanguage>\n" % self._default_language)
        if self._current_language:
            file.write(u"\t\t<CurrentLanguage>%s</CurrentLanguage>\n" % self._current_language)
        file.write(u"\t</Information>\n")

        self._objects.compose(ident=u"\t", file=file, shorter=shorter)
        self._actions.compose(ident=u"\t", file=file)

        file.write(u"\t<Structure>\n")
        for container in self._objects.itervalues():
            container.structure.compose(ident=u"\t\t", file=file)
        file.write(u"\t</Structure>\n")

        if not shorter:
            extension = self.scripting_extension
            filenames = managers.file_manager.list(file_access.LIBRARY, self._id)
            names = {name[:-3] for name in filenames if name.endswith(extension)}
            if names:
                file.write(u"\t<Libraries>\n")
                for name in names:
                    file.write(u"\t\t<Library Name=\"%s\">\n" % name)
                    with managers.file_manager.open(file_access.LIBRARY, self._id, name + extension,
                            mode="rU", encoding="utf8") as library_file:
                        library_source_code = library_file.read()
                    file.write(u"%s\n" % library_source_code.encode("cdata"))
                    file.write(u"\t\t</Library>\n")
                file.write(u"\t</Libraries>\n")

        if self._sentences:
            file.write(u"\t<Languages>\n")
            for language_code in sorted(self._sentences):
                language_sentences = self._sentences[language_code]
                if language_sentences:
                    file.write(u"\t\t<Language Code=\"%s\">\n" % language_code)
                    for sentence_code in sorted(language_sentences):
                        file.write(u"\t\t\t<Sentence ID=\"%03d\">%s</Sentence>\n" % (
                            sentence_code, language_sentences[sentence_code].encode("xml")))
                    file.write(u"\t\t</Language>\n")
            file.write(u"\t</Languages>\n")

        if not shorter:
            ids = managers.resource_manager.list_resources(self._id)
            if ids:
                file.write(u"\t<Resources>\n")
                for id in ids:
                    resource = managers.resource_manager.get_resource(self._id, id)
                    # TODO: Investigate this condition
                    if resource.label == "":
                        try:
                            data = resource.get_data()
                        except:
                            continue
                        data = base64.b64encode(data)
                        file.write(u"\t\t<Resource ID=\"%s\" Type=\"%s\" Name=\"%s\">%s</Resource>\n" % (
                            id, resource.res_format, resource.name, data))
                file.write(u"\t</Resources>\n")

            ids = managers.database_manager.list_databases(self._id)
            if ids:
                file.write(u"\t<Databases>\n")
                for id in ids:
                    query = VDOM_sql_query(self._id, id, "VACUUM")
                    query.commit()
                    query.close()

                    query = VDOM_sql_query(self._id, id, "PRAGMA journal_mode=WAL;")
                    query.commit()
                    query.close()

                    database = managers.database_manager.get_database(self._id, id)
                    data = managers.database_manager.backup_database(self._id, id)
                    if database.name != "" and data:
                        data = base64.b64encode(data)
                        file.write(u"\t\t<Database ID=\"%s\" Name=\"%s\" Type=\"sqlite\">%s</Database>\n" % (
                            database.id, database.name, data))
                file.write(u"\t</Databases>\n")

        if self._bindings or self._events.catalog:
            file.write(u"\t<E2VDOM>\n")
            self._bindings.compose(ident=u"\t\t", file=file)
            self._events.catalog.compose(ident=u"\t\t", file=file)
            file.write(u"\t</E2VDOM>\n")

        groups, users = defaultdict(list), defaultdict(list)

        def iterate():
            yield self._id
            for object in self._objects.itervalues():
                yield object.id

        for object_id in iterate():
            try:
                acl = managers.acl_manager.acl[object_id]
            except KeyError:
                continue
            for name, value in acl.iteritems():
                item = (object_id, u",".join(map(str, value.keys())))
                group = managers.user_manager.get_group_by_name(name)
                if group and not group.system:
                    groups[group].append(item)
                user = managers.user_manager.get_user_object(name)
                if user and not user.system:
                    users[user].append(item)

        if groups or users:
            file.write(u"\t<Security>\n")
            if groups:
                file.write(u"\t\t<Groups>\n")
                for group, items in groups.iteritems():
                    file.write(u"\t\t\t<Group>\n")
                    file.write(u"\t\t\t\t<Name>%s</Name>\n" % group.login.encode("xml"))
                    file.write(u"\t\t\t\t<Description>%s</Description>\n" % group.description.encode("xml"))
                    file.write(u"\t\t\t\t<Rights>\n")
                    for item in items:
                        file.write(u"\t\t\t\t\t<Right Target=\"%s\" Access=\"%s\"/>\n" % item)
                    file.write(u"\t\t\t\t</Rights>\n")
                    file.write(u"\t\t\t</Group>\n")
                file.write(u"\t\t</Groups>\n")
            if users:
                file.write(u"\t\t<Users>\n")
                for user, items in users.iteritems():
                    file.write(u"\t\t\t<User>\n")
                    file.write(u"\t\t\t\t<Login>%s</Login>\n" % user.login.encode("xml"))
                    file.write(u"\t\t\t\t<Password>%s</Password>\n" % user.password.encode("xml"))
                    file.write(u"\t\t\t\t<FirstName>%s</FirstName>\n" % user.first_name.encode("xml"))
                    file.write(u"\t\t\t\t<LastName>%s</LastName>\n" % user.last_name.encode("xml"))
                    file.write(u"\t\t\t\t<Email>%s</Email>\n" % user.email.encode("xml"))
                    file.write(u"\t\t\t\t<SecurityLevel>%s</SecurityLevel>\n" % user.security_level.encode("xml"))
                    file.write(u"\t\t\t\t<MemberOf>%s</MemberOf>\n" % u",".join(user.member_of).encode("xml"))
                    file.write(u"\t\t\t\t<Rights>\n")
                    for item in items:
                        file.write(u"\t\t\t\t\t<Right Target=\"%s\" Access=\"%s\"/>\n" % item)
                    file.write(u"\t\t\t\t</Rights>\n")
                    file.write(u"\t\t\t</User>\n")
                file.write(u"\t\t</Users>\n")
            file.write(u"\t</Security>\n")

        file.write(u"</Application>\n")

    def autosave(self):
        if not settings.AUTOSAVE_APPLICATIONS:
            log.write("Unable to auto save %s due to settings disallow" % self)

        if not self._save_queue:
            log.write("Autosave %s" % self)
            self._save_queue = True
            managers.memory.schedule(self)

    def save(self, async=False):
        if settings.ALLOW_TO_CHANGE is not None:
            if self._id not in settings.ALLOW_TO_CHANGE:
                log.write("Unable to save %s due to settings disallow" % self)
                return

        if async:
            if not self._save_queue:
                self._save_queue = True
                managers.memory.schedule(self)
        else:
            with self.lock:
                self._save_queue = False
                log.write("Save %s" % self)
                with managers.file_manager.open(file_access.APPLICATION, self._id, settings.APPLICATION_FILENAME,
                        mode="w", encoding="utf8") as file:
                    self.compose(file=file, shorter=True)
                self._changes = False

    def export(self, filename):
        with self.lock:
            with managers.file_manager.open(file_access.FILE, filename,
                    mode="w", encoding="utf8") as file:
                self.compose(file=file)

    # unsafe
    def uninstall(self, remove_zero_resources=True, remove_databases=True, remove_storage=True):
        # if not managers.acl_manager.session_user_has_access2(application_id, application_id, security.delete_application):
        #     raise VDOM_exception_sec(_("Deleting application is not allowed"))

        # remove from save queue
        if self._save_queue:
            managers.memory.unschedule(self)

        # unload application
        managers.memory.applications.unload(self._id)

        # NOTE: currently not supported
        # on_uninstall = application.global_actions[APPLICATION_SECTION][APPLICATION_SECTION + ON_UNINSTALL]
        # if on_uninstall.code:
        #     __import__(application.id)
        #     try:
        #         managers.engine.special(application, on_uninstall, namespace={})
        #     except Exception as e:
        #         debug("Error while executing application onuninstall action: %s" % str(e))
        #         traceback.print_exc(file=debugfile)
        # NOTE: new code
        # handler = application.global_actions.get("on_uninstall")
        # if handler:
        #     managers.engine.execute(handler, namespace={})

        # delete objects's resources
        for object in self._objects.catalog.itervalues():
            managers.resource_manager.invalidate_resources(object.id)

        # delete resources
        # NOTE: managers.resource_manager.invalidate_resources(self._id)
        # TODO: check this later...
        uuids = managers.resource_manager.list_resources(self._id)
        for uuid in uuids:
            resource = managers.resource_manager.get_resource(self._id, uuid)
            if resource and (len(resource.dependences) or remove_zero_resources):
                log.debug("Remove resource %s" % uuid)
                try:
                    managers.resource_manager.delete_resource(None, uuid, True)
                except Exception as error:
                    log.error("Error removing resource %s: %s" % (uuid, error))
            else:
                log.debug("Keep resource %s" % uuid)

        # delete databases
        if remove_databases:
            managers.database_manager.delete_database(self._id)

        # remove files
        managers.memory.cleanup_application(self._id,
            remove_databases=remove_databases, remove_storage=remove_storage)

    def unimport_libraries(self):
        with self.lock:
            for name in self._libraries:
                module_name = "%s.%s" % (self.id, name)
                if module_name in sys.modules:
                    sys.modules.pop(module_name)

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, (
            "application",
            ":".join(filter(None, (self._id, self._name.lower()))))))
