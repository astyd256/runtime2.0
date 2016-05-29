
import re
from .. import levels
from .multiline import MultilineLogFormatter


class PrefixingLogFormatter(MultilineLogFormatter):

    PREFIXES = levels.PREFIXES
    PREFIXES_REGEX = re.compile("(?:\[(.+)\](\s+))?(?:%s)?" %
        "|".join("(%s)" % (prefix or "$") for prefix in PREFIXES), re.IGNORECASE)

    def _make_caption(self, module, level, *values):
        return super(PrefixingLogFormatter, self)._make_caption(*values) + \
            ("[%s] " % module if module else "") + self.PREFIXES[level]

    def parse(self, data):
        values = super(PrefixingLogFormatter, self).parse(data)
        fields, message = values[:-1], values[-1]
        match = self.PREFIXES_REGEX.match(message)
        if match:
            module, level = match.group(1) or "", match.lastindex - 3 if match.lastindex > 2 else levels.MESSAGE
            message = message[match.end():].replace(match.group(0), "")
        else:
            module, level = "", levels.MESSAGE
        return (module, level) + fields + (message,)
