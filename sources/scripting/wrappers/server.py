
from inspect import iscode, isroutine

import managers
import version
import vscript

from uuid import uuid4
from vscript.engine import vcompile, vexecute, vevaluate
from mailing.message import Message, MailAttachment as Attachment
from mailing.pop import VDOM_Pop3_client


class VDOM_vscript_libraries(object):

    def __init__(self, owner):
        self._owner = owner

    def register(self, name, source, data=None, environment=None, context=None):
        if context is None:
            raise Exception("Require context")

        if isroutine(source):

            def initializer(context, name, namespace):
                code = source(context, name)
                if isinstance(code, tuple):
                    code, data = code
                self._owner.execute(code, data, namespace=namespace, environment=environment)

        else:
            if iscode(source):
                code = source
            else:
                code, data = self._owner.compile(source, environment=environment)

            def initializer(context, name, namespace):
                self._owner.execute(code, data, namespace=namespace, environment=environment)

        managers.import_manager.register(context, name, initializer)

    def unregister(self, name=None, context=None):
        if context is None:
            raise Exception("Require context")
        managers.import_manager.unregister(context, name)

    def exists(self, name=None, context=None):
        if context is None:
            return False
        else:
            return managers.import_manager.lookup(context, name) is not None


class VDOM_vscript(object):

    def __init__(self):
        self._libraries = VDOM_vscript_libraries(self)

    libraries = property(lambda self: self._libraries)

    error = property(lambda self: vscript.errors.generic)

    variant = property(lambda self: vscript.variant)
    integer = property(lambda self: vscript.integer)
    string = property(lambda self: vscript.string)
    generic = property(lambda self: vscript.generic)

    vfunction = property(lambda self: vscript.vfunction)
    vsub = property(lambda self: vscript.vsub)
    vproperty = property(lambda self: vscript.vproperty)
    vcollection = property(lambda self: vscript.vcollection)

    def compile(self, source=None, let=None, set=None, use=None,
            anyway=False, context=None, environment=None, **keywords):
        if environment is None:
            environment = {"v_%s" % name: value for name, value in keywords.iteritems()}
        package = None if context is None else ":".join((managers.engine.application.id, context))
        return vcompile(source, let, set, package=package, environment=environment, use=use, anyway=anyway)

    def execute(self, source_or_code, data=None, use=None,
            anyway=False, context=None, environment=None, namespace=None, **keywords):
        if environment is None:
            environment = {"v_%s" % name: value for name, value in keywords.iteritems()}
        if iscode(source_or_code):
            code = source_or_code
        else:
            code, data = self.compile(source_or_code, use=use,
                anyway=anyway, context=context, environment=environment, **keywords)
        vexecute(code, data, use=use, environment=environment, namespace=namespace)

    def evaluate(self, let=None, set=None, use=None,
            anyway=False, context=None, environment=None, namespace=None, result=None, **keywords):
        if environment is None:
            environment = {"v_%s" % name: value for name, value in keywords.iteritems()}
        if iscode(let or set):
            code = let or set
        else:
            code, data = self.compile(let=let, set=set, use=use,
                anyway=anyway, context=context, environment=environment, **keywords)
        return vevaluate(code, data, use=use, environment=environment, namespace=namespace, result=result)


class VDOM_mailer(object):

    def send(self, *args, **kw):
        return managers.email_manager.send(*args, **kw)

    def check(self, _id):
        return managers.email_manager.check(_id)

    def check_connection(self):
        return managers.email_manager.check_connection()

    def cancel(self, _id):
        return managers.email_manager.cancel(_id)

    def status(self):
        return managers.email_manager.status()

    def clear_queue(self):
        managers.email_manager.clear_queue()

    def get_queue(self):
        return managers.email_manager.get_queue()

    def pop3_connect(self, server, port=110, secure=False):
        return VDOM_Pop3_client(server, port, secure)

    Message = Message
    Attachment = Attachment
    smtp_server = property(lambda self: managers.email_manager.smtp_server)
    smtp_port = property(lambda self: managers.email_manager.smtp_port)
    smtp_user = property(lambda self: managers.email_manager.smtp_user)
    smtp_pass = property(lambda self: managers.email_manager.smtp_pass)
    smtp_sender = property(lambda self: managers.email_manager.smtp_sender)
    use_ssl = property(lambda self: managers.email_manager.use_ssl)


class VDOM_server(object):

    def __init__(self):
        self._vscript = VDOM_vscript()
        self._mailer = VDOM_mailer()

    def _get_version(self):
        # return version.VDOM_server_version
        return version.SERVER_VERSION

    def _get_guid(self):
        # return utils.uuid.uuid4()
        return uuid4()

    version = property(_get_version)
    # mailer=property(lambda self: managers.email_manager)
    mailer = property(lambda self: self._mailer)
    guid = property(_get_guid)
    vscript = property(lambda self: self._vscript)
