

import re


DIGITS = set("0123456789")
PATTERN = re.compile(".+?(\d+)")


class UniqueNameDictionary(dict):

    _cache = None

    def generate(self, origin, prototype):
        if self._cache and self._cache[0] == (origin or prototype):
            common, padding, index = self._cache[1:]
            simple = True
        else:
            if origin and origin[-1] in DIGITS:
                value = PATTERN.match(origin).group(1)
                length = len(value)
                common = origin[:-length]
                padding = length if value[0] == "0" else 0
                index = int(value) + 1
            else:
                common = origin or prototype
                padding = 0
                index = 1
            simple = len(self) < 7  # force simple on small numbers

        if simple:
            while 1:
                name = "%s%0*d" % (common, padding, index)
                if name not in self:
                    self._cache = origin, common, padding, index + 1
                    return name
                index += 1
        else:
            left, step, previous = index, 1, 0
            while 1:
                name = "%s%0*d" % (common, padding, index)
                if name not in self:
                    break
                left = index
                index += step
                step, previous = step + previous, step
            if step == 1:
                self._cache = origin, common, padding, index + 1
                return name
            right = index
            while 1:
                index = (left + 1 + right) // 2
                name = "%s%0*d" % (common, padding, index)
                if name in self:
                    left = index
                else:
                    right = index
                    if right == left + 1:
                        self._cache = origin, common, padding, index + 1
                        return name

    def drop(self):
        if self._cache:
            del self._cache
