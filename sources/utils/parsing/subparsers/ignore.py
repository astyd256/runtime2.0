
from ..auxiliary import subparser


@subparser
def ignore(self, selector, iterator):
    """
    Ignore inner elements
    """

    context = \
        self._parser.StartElementHandler, \
        self._parser.EndElementHandler

    def element(name, attributes):
        context = \
            self._parser.StartElementHandler, \
            self._parser.EndElementHandler

        def element(name, attributes):
            context = self._parser.EndElementHandler

            def close_element(name):
                self._parser.EndElementHandler = context

            self._parser.EndElementHandler = close_element

        def close_element(name):
            self._parser.StartElementHandler, \
                self._parser.EndElementHandler = context

        self._parser.StartElementHandler = element
        self._parser.EndElementHandler = close_element

    def close_element(name):
        if iterator:
            try:
                iterator.next()
            except StopIteration:
                pass

        self._parser.StartElementHandler, \
            self._parser.EndElementHandler = context

    self._parser.StartElementHandler = element
    self._parser.EndElementHandler = close_element


IGNORE = ignore
