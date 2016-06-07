
from contextlib import contextmanager
from threading import local, current_thread
import managers
from logs import log
from memory import COMPUTE_CONTEXT, RENDER_CONTEXT, WYSIWYG_CONTEXT
from .exceptions import RenderTermination


class Engine(object):

    def __init__(self):
        self._storage = local()

    application = property(lambda self: getattr(self._storage, "application", None))

    def select(self, application=None):
        if isinstance(application, basestring):
            application = managers.memory.applications[application]
        previous = getattr(self._storage, "application", None)
        if application is not previous:
            log.write("Select %s" % (application or "no application"))
            self._storage.application = application
            # TODO: check this thread using
            current_thread().application = application.id if application else None
        return previous

    @contextmanager
    def context(self, application=None):
        if application:
            previous = self.select(application)
        try:
            yield
        finally:
            if application:
                self.select(previous)

    def compute(self, object, parent=None):
        log.write("Compute %s" % object)
        previous = self.select(object.application)
        try:
            instance = object.factory(COMPUTE_CONTEXT)(parent)
            instance.recompute()
        finally:
            self.select(previous)

    def render(self, object, parent=None, render_type=None):
        log.write("Render %s" % object)
        previous = self.select(object.application)
        try:
            instance = object.factory(RENDER_CONTEXT)(parent)
            instance.execute(managers.request_manager.get_request().session().context)
            return instance.render()
        except RenderTermination:
            return ""
        finally:
            self.select(previous)

    def wysiwyg(self, object, parent=None):
        log.write("Wysiwyg %s" % object)
        previous = self.select(object.application)
        try:
            instance = object.factory(WYSIWYG_CONTEXT)(parent)
            return instance.wysiwyg()
        finally:
            self.select(previous)

    def execute(self, action, parent=None, context=None, render=None):
        log.write("Execute %s" % action)
        previous = self.select(action.owner.application)
        try:
            if action.owner.is_application:
                action.execute(None, managers.request_manager.get_request().session().context)
            else:
                instance = action.owner.factory(context or action.id)(parent)
                instance.execute(managers.request_manager.get_request().session().context)
                return instance.separate_render() if render else None
        except RenderTermination:
            return "" if render else None
        finally:
            self.select(previous)

    def terminate(self):
        log.write("Terminate render")
        raise RenderTermination


VDOM_engine = Engine
