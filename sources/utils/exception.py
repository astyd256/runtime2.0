
class VDOM_exception(Exception):

    def __init__(self, desc=""):
        self.__str = desc

    def __str__(self):
        return self.__str

    def __repr__(self):
        return self.__str


class VDOM_exception_element(VDOM_exception): # SOAP

    def __init__(self, name):
        VDOM_exception.__init__(self, "invalid element: \"%s\"" % name)


class VDOM_exception_param(VDOM_exception): # SOAP
    pass


class VDOM_exception_sec(VDOM_exception):  # for security checks
    pass


class VDOM_exception_file_access(VDOM_exception): # scripting

    def __init__(self, s):
        VDOM_exception.__init__(self, "VDOM file access error: " + s)


class VDOM_mailserver_invalid_index(VDOM_exception):

    def __init__(self, index):
        VDOM_exception.__init__(self, "Mailserver have no messaeg with index: \"%s\"" % index)


class VDOMServiceCallError(Exception):
    pass


class VDOMSecureServerError(VDOM_exception):
    pass


class VDOMDatabaseAccessError(VDOM_exception):
    def __init__(self, s):
        VDOM_exception.__init__(self, "Database request failed: " + s)
