
class AbortingError(Exception):
    pass


# generic class

class ParsingException(Exception):

    def __init__(self, message, offset=None, lineno=None, column=None):
        super(ParsingException, self).__init__(message)
        self.offset = offset
        self.lineno = lineno
        self.column = column


# parser errors

class UnableToChangeError(ParsingException):

    def __init__(self, name):
        super(UnableToChangeError, self).__init__(u"Unable to change %s when parsing" % name)


# expat error wrappers

class OutOfMemoryError(ParsingException):

    def __init__(self):
        super(OutOfMemoryError, self).__init__(u"Out of memory")


class JunkAfterDocumentError(ParsingException):

    def __init__(self):
        super(JunkAfterDocumentError, self).__init__(u"Junk after document")


# unexpected entities

class UnexpectedElementError(ParsingException):

    def __init__(self, name, attributes=None):
        super(UnexpectedElementError, self).__init__(u"Unexpected \"%s\" element" % name)


class UnexpectedAttributeError(ParsingException):

    def __init__(self, name):
        super(UnexpectedAttributeError, self).__init__(u"Unexpected \"%s\" atribute" % name)


# incorrect entities

class UnexpectedElementValueError(ParsingException):

    def __init__(self, name):
        super(UnexpectedElementValueError, self).__init__(u"Unexpected \"%s\" element value or contents" % name)


class UnexpectedAttributeValueError(ParsingException):

    def __init__(self, name):
        super(UnexpectedAttributeValueError, self).__init__(u"Unexpected \"%s\" attribute value" % name)


# missing entities

class MissingElementError(ParsingException):

    def __init__(self, name):
        super(MissingElementError, self).__init__(u"Missing \"%s\" element" % name)


class MissingAttributeError(ParsingException):

    def __init__(self, name):
        super(MissingAttributeError, self).__init__(u"Missing \"%s\" atribute" % name)


# memory sections

class SectionMustPrecedeError(ParsingException):

    def __init__(self, name):
        super(SectionMustPrecedeError, self).__init__(u"%s section must precede" % name)


class MissingSectionError(ParsingException):

    def __init__(self, name):
        super(MissingSectionError, self).__init__(u"Missing %s section" % name)
