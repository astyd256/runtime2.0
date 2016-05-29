
import os
import re
from .formatter import LogFormatter


class TabbingLogFormatter(LogFormatter):

    CRLF_N_TAB_REGEX = re.compile("\t|\n|\r\n|\r")

    def format(self, *arguments):
        return ("\t".join(self.CRLF_N_TAB_REGEX.sub(" ", argument) for argument in arguments)).rstrip() + os.linesep

    FIND_REGEX = re.compile("\n|\r\n|\r")

    def finditer(self, data):
        for match in self.FIND_REGEX.finditer(data):
            yield match.end(0)

    def parse(self, entry):
        return (entry.rstrip("\r\n") + "\n").split("\t")
