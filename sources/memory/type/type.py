
from threading import RLock
from collections import defaultdict
from io import StringIO

import settings
import file_access
import scripting
import managers

from utils.id import guid2mod
from utils.properties import lazy, roproperty, rwproperty

from ..constants import PYTHON_LANGUAGE, PYTHON_EXTENSION, NON_CONTAINER
from ..generic import MemoryBase
from ..auxiliary import copy_as_base64
from .attributes import MemoryTypeAttributes
from .events import MemoryTypeUserInterfaceEvents, MemoryTypeObjectEvents
from .actions import MemoryTypeActions


NOT_LOADED = "NOT LOADED"


class MemoryTypeSketch(MemoryBase):

    @lazy
    def _executable(self):
        from scripting.executable import select_module_class
        return select_module_class(PYTHON_LANGUAGE)(self)

    @lazy
    def _module_name(self):
        return guid2mod(self._id)

    @lazy
    def _module(self):
        return __import__(self._module_name)

    @lazy
    def _klass(self):
        return self._module.__dict__[self._class_name]

    def __init__(self, callback):
        self._callback = callback
        self._lock = RLock()

        self._id = None
        self._name = None
        self._display_name = None
        self._class_name = None
        self._description = u""
        self._category = u"Standard"
        self._interface_type = 1
        self._icon = u""
        self._editor_icon = u""
        self._structure_icon = u""
        self._dynamic = 0
        self._moveable = 1
        self._resizable = 1
        self._optimization_priority = 1
        self._container = NON_CONTAINER
        self._containers = []
        self._render_type = u""
        self._http_content_type = u""
        self._remote_methods = []
        self._handlers = []
        self._languages = []
        self._version = u"1"

        self._attributes = MemoryTypeAttributes(self)
        self._sentences = defaultdict(dict)
        self._resources = {}
        self._libraries = defaultdict(list)
        self._external_libraries = defaultdict(list)
        self._user_interface_events = MemoryTypeUserInterfaceEvents(self)
        self._object_events = MemoryTypeObjectEvents(self)
        self._actions = MemoryTypeActions(self)

        self._class = None

    def _set_id(self, value):
        self._id = value
        if "_module_name" is self.__dict__:
            del self._module_name

    lock = roproperty("_lock")

    id = rwproperty("_id", _set_id)
    name = rwproperty("_name")
    display_name = rwproperty("_display_name")
    class_name = rwproperty("_class_name")
    description = rwproperty("_description")
    category = rwproperty("_category")
    interface_type = rwproperty("_interface_type")
    icon = rwproperty("_icon")
    editor_icon = rwproperty("_editor_icon")
    structure_icon = rwproperty("_structure_icon")
    dynamic = rwproperty("_dynamic")
    moveable = rwproperty("_moveable")
    resizable = rwproperty("_resizable")
    optimization_priority = rwproperty("_optimization_priority")
    container = rwproperty("_container")
    containers = rwproperty("_containers")
    render_type = rwproperty("_render_type")
    http_content_type = rwproperty("_http_content_type")
    remote_methods = rwproperty("_remote_methods")
    handlers = rwproperty("_handlers")
    languages = rwproperty("_languages")
    version = rwproperty("_version")

    attributes = roproperty("_attributes")
    sentences = roproperty("_sentences")
    resources = roproperty("_resources")
    libraries = roproperty("_libraries")
    external_libraries = roproperty("_external_libraries")
    user_interface_events = roproperty("_user_interface_events")
    object_events = roproperty("_object_events")
    actions = roproperty("_actions")

    executable = roproperty("_executable")
    module_name = roproperty("_module_name")
    module = roproperty("_module")
    klass = roproperty("_klass")

    def __invert__(self):
        if self._id is None:
            raise Exception(u"Type require identifier")
        if self._name is None:
            raise Exception(u"Type require name")
        if self._display_name is None:
            self._display_name = self._name
        if self._class_name is None:
            self._class_name = u"_".join("VDOM", self._name)

        self.__class__ = MemoryType
        self._callback = self._callback(self)
        return self

    def __str__(self):
        return " ".join(filter(None, ("type", ":".join(filter(None, (self._id, self._name))), "sketch")))


class MemoryType(MemoryTypeSketch):

    def __init__(self):
        raise Exception(u"Use 'new' to create new type")

    id = roproperty("_id")
    module_name = roproperty("_module_name")
    name = roproperty("_name")
    display_name = roproperty("_display_name")
    class_name = roproperty("_class_name")
    description = roproperty("_description")
    version = roproperty("_version")
    category = roproperty("_category")
    interface_type = roproperty("_interface_type")
    icon = roproperty("_icon")
    editor_icon = roproperty("_editor_icon")
    structure_icon = roproperty("_structure_icon")
    dynamic = roproperty("_dynamic")
    moveable = roproperty("_moveable")
    resizable = roproperty("_resizable")
    optimization_priority = roproperty("_optimization_priority")
    container = roproperty("_container")
    containers = roproperty("_containers")
    render_type = roproperty("_render_type")
    http_content_type = roproperty("_http_content_type")
    remote_methods = roproperty("_remote_methods")
    handlers = roproperty("_handlers")
    languages = roproperty("_languages")

    # unsafe
    def compose(self, file=None, shorter=False):
        if not file:
            file = StringIO()
            self.compose(file=file, shorter=True)
            return file.getvalue()

        file.write(u"<?xml version=\"1.0\" encoding=\"utf-8\"?>\n")
        file.write(u"<Type>\n")

        file.write(u"\t<Information>\n")
        file.write(u"\t\t<ID>%s</ID>\n" % self._id)
        file.write(u"\t\t<Name>%s</Name>\n" % self._name.encode("xml"))
        if self._display_name:
            file.write(u"\t\t<DisplayName>%s</DisplayName>\n" % self._display_name.encode("xml"))
        file.write(u"\t\t<ClassName>%s</ClassName>\n" % self._class_name.encode("xml"))
        if self._description:
            file.write(u"\t\t<Description>%s</Description>\n" % self._description.encode("xml"))
        file.write(u"\t\t<Version>%s</Version>\n" % self._version)
        file.write(u"\t\t<Category>%s</Category>\n" % self._category.encode("xml"))
        file.write(u"\t\t<InterfaceType>%s</InterfaceType>\n" % self._interface_type)
        if self._icon:
            file.write(u"\t\t<Icon>%s</Icon>\n" % self._icon)
        if self._editor_icon:
            file.write(u"\t\t<EditorIcon>%s</EditorIcon>\n" % self._editor_icon)
        if self._structure_icon:
            file.write(u"\t\t<StructureIcon>%s</StructureIcon>\n" % self._structure_icon)
        file.write(u"\t\t<Dynamic>%s</Dynamic>\n" % self._dynamic)
        file.write(u"\t\t<Moveable>%s</Moveable>\n" % self._moveable)
        file.write(u"\t\t<Resizable>%s</Resizable>\n" % self._resizable)
        file.write(u"\t\t<OptimizationPriority>%s</OptimizationPriority>\n" % self._optimization_priority)
        file.write(u"\t\t<Container>%s</Container>\n" % self._container)
        if self._containers:
            file.write(u"\t\t<Containers>%s</Containers>\n" % u", ".join(self._containers))
        if self._render_type:
            file.write(u"\t\t<RenderType>%s</RenderType>\n" % self._render_type)
        if self._http_content_type:
            file.write(u"\t\t<HTTPContentType>%s</HTTPContentType>\n" % self._http_content_type.encode("xml"))
        if self._remote_methods:
            file.write(u"\t\t<RemoteMethods>%s</RemoteMethods>\n" % self._remote_methods.encode("xml"))
        if self._handlers:
            file.write(u"\t\t<Handlers>%s</Handlers>\n" % u", ".join(self._handlers))
        if self._languages:
            file.write(u"\t\t<Languages>%s</Languages>\n" % u", ".join(self._languages))
        file.write(u"\t</Information>\n")

        self._attributes.compose(ident=u"\t", file=file)

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
            ids = sorted(managers.resource_manager.list_resources(self._id))
            if ids:
                file.write(u"\t<Resources>\n")
                for id in ids:
                    resource = managers.resource_manager.get_resource(self._id, id)
                    if resource.label == "":
                        try:
                            resource_file = resource.get_fd()
                        except:
                            continue
                        file.write(u"\t\t<Resource ID=\"%s\" Type=\"%s\" Name=\"%s\">\n" % (id, resource.res_format, resource.name))
                        copy_as_base64(file, resource_file, indent=u"\t\t\t")
                        file.write(u"\t\t</Resource>\n")
                file.write(u"\t</Resources>\n")

        if not shorter:
            source_code = managers.file_manager.read(file_access.MODULE, self._id,
                settings.TYPE_MODULE_NAME + PYTHON_EXTENSION, encoding="utf8")
            file.write(u"\t<SourceCode>\n")
            file.write(u"%s\n" % source_code.encode("cdata"))
            file.write(u"\t</SourceCode>\n")

        if self._libraries or self._external_libraries:
            file.write(u"\t<Libraries>\n")
            for library_target, libraries in self._libraries.iteritems():
                for library in libraries:
                    file.write(u"\t\t<Library Target=\"%s\">%s</Library>\n" % (library_target, library.encode("cdata")))
            for library_target, libraries in self._external_libraries.iteritems():
                for library in libraries:
                    file.write(u"\t\t<ExternalLibrary Target=\"%s\">%s</ExternalLibrary>\n" % (library_target, library.encode("cdata")))
            file.write(u"\t</Libraries>\n")

        if self._user_interface_events or self._object_events or self._actions:
            file.write(u"\t<E2VDOM>\n")
            file.write(u"\t\t<Events>\n")
            self._user_interface_events.compose(ident=u"\t\t\t", file=file)
            self._object_events.compose(ident=u"\t\t\t", file=file)
            file.write(u"\t\t</Events>\n")
            self._actions.compose(ident=u"\t\t", file=file)
            file.write(u"\t</E2VDOM>\n")

        file.write(u"</Type>\n")

    def save(self, async=False):
        if async:
            managers.memory.schedule(self)
        else:
            with managers.file_manager.open(file_access.TYPE, self._id, settings.TYPE_FILENAME,
                    mode="w", encoding="utf8") as file:
                self.compose(file=file, shorter=True)

    def export(self, filename):
        with managers.file_manager.open(file_access.FILE, None, filename,
                mode="w", encoding="utf8") as file:
            self.compose(file=file)

    def uninstall(self):
        managers.memory.types.unload(self._id)
        managers.resource_manager.invalidate_resources(self._id)
        managers.memory.cleanup_type(self._id)

    def factory(self, context, probe=False):
        with self._lock:
            if self._class is None:
                if probe:
                    return None
                self._class = scripting.create_type_object(self)
            return self._class

    def __invert__(self):
        raise NotImplementedError

    def __str__(self):
        return " ".join(filter(None, ("type", ":".join(filter(None, (self._id, self._name))))))
