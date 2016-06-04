
from importlib import import_module
from threading import RLock
from logs import log

# from utils.properties import roproperty
# from utils.tracing import format_exception_trace
# import SOAPpy

# import managers
# from soap.errors import *
# import utils
# from utils.exception import *
# from utils.exception import VDOM_exception_handler


UNKNOWN = "UNKNOWN"


roproperty = import_module("utils.properties").roproperty
format_exception_trace = import_module("utils.tracing").format_exception_trace


class DispatcherEntry(object):

    def __init__(self, entries, type):
        self._entries = entries
        self._type = type
        self._module = None
        self._handlers = {}

    type = roproperty("_type")
    handlers = roproperty("_handlers")

    def new(self, name):
        self._handlers[name] = UNKNOWN

    def __getitem__(self, name):
        handler = self._handlers.get(name)
        if handler is UNKNOWN:
            with self._entries._lock:
                handler = self._handlers.get(name)
                if handler is UNKNOWN:
                    if not self._module:
                        try:
                            self._module = __import__(self._type.module_name)
                        except:
                            log.error("[Dispatcher] Unable to import module: %s" % format_exception_trace())
                            self._module = {"__doc__": "Unable to load %s" % self._type.module_name}
                    self._handlers[name] = handler = getattr(self._module, name, None)
        return handler


class DispatcherEntries(object):

    def __init__(self):
        self._lock = RLock()
        self._entries = {}

    def __getitem__(self, type):
        try:
            return self._entries[type]
        except KeyError:
            with self._lock:
                entry = self._entries.get(type)
                if not entry:
                    self._entries[type] = entry = DispatcherEntry(self, type)
                return entry


class Dispatcher(object):

    def __init__(self):
        self._entries = DispatcherEntries()
        # self.__remote_index = {}

    def add_handler(self, type, name):
        self._entries[type].new(name)

    def add_remote_method(self, type_id, func_name):
        raise NotImplemented
        # if type_id not in self.__remote_index:
        #     self.__remote_index[type_id] = []
        # self.__remote_index[type_id].append(func_name)

    # Underscores are used to avoid name conflicts with keywords
    def dispatch_handler(self, _object_, _name_, *arguments, **keywords):
        handler = self._entries[_object_.type][_name_]
        if handler:
            handler(_object_, *arguments, **keywords)

    def dispatch_remote(self, app_id, object_id, func_name, xml_param, session_id=None):
        raise NotImplemented
        # try:
        #     object = managers.memory.applications[app_id].objects[object_id]
        #     # CHECK: object = managers.xml_manager.search_object(app_id, object_id)
        #     if object.type.id in self.__remote_index and func_name in self.__remote_index[object.type.id]:
        #         module = __import__(utils.id.guid2mod(object.type.id))
        #         if func_name in module.__dict__:
        #             if session_id:
        #                 return getattr(module, func_name)(app_id, object_id, xml_param, session_id)
        #             else:
        #                 return getattr(module, func_name)(app_id, object_id, xml_param)
        # except Exception, e:
        #     if getattr(e, "message", None) and isinstance(e.message, unicode):
        #         msg = unicode(e).encode("utf8")
        #     else:
        #         msg = str(e)

        #     raise SOAPpy.faultType(remote_method_call_error, _("Remote method call error"), msg)
        #     # return "<Error><![CDATA[%s]]></Error>"%str(e)
        # raise SOAPpy.faultType(remote_method_call_error, _("Handler not found"), str(func_name))
        # # return "<Error><![CDATA[Handler not found]]></Error>"

    def dispatch_action(self, app_id, object_id, func_name, xml_param, xml_data):
        raise NotImplemented
        # try:
        #     request = managers.request_manager.get_request()
        #     request.arguments().arguments({"xml_param": [xml_param], "xml_data": [xml_data]})
        #     app = managers.memory.get_application(app_id)  # CHECK: app = managers.xml_manager.get_application(app_id)
        #     obj = app.search_object(object_id)
        #     # managers.engine.execute(app, obj, None, func_name, True)
        #     # TODO: Check situation if object hasn't such action
        #     managers.engine.execute(obj.actions[func_name])
        #     ret = request.session().value("response")
        #     request.session().remove("response")
        #     return ret or ""
        # except Exception, e:
        #     if getattr(e, "message", None) and isinstance(e.message, unicode):
        #         msg = unicode(e).encode("utf8")
        #     else:
        #         msg = str(e)
        #     raise SOAPpy.faultType(remote_method_call_error, _("Action call error"), msg)
        # raise SOAPpy.faultType(remote_method_call_error, _("Handler not found"), str(func_name))


VDOM_dispatcher = Dispatcher
