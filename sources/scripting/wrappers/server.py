
import managers
import version
from uuid import uuid4
from vscript.engine import vcompile, vexecute, vevaluate
from mailing.message import Message, MailAttachment as Attachment
from mailing.pop import VDOM_Pop3_client


class VDOM_vscript(object):

    def execute(self, source, use=None, **keywords):
        environment = {"v_%s" % name: value for name, value in keywords.iteritems()}
        code, vsource = vcompile(source, environment=environment, use=use)
        vexecute(code, vsource, environment=environment, use=use)

    def evaluate(self, let=None, set=None, use=None, result=None, **keywords):
        environment = {"v_%s" % name: value for name, value in keywords.iteritems()}
        code, vsource = vcompile(let=let, set=set, environment=environment, use=use)
        return vevaluate(code, vsource, environment=environment, use=use, result=result)


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
