
from utils.parsing import VALUE
from .exceptions import OptionError


class WatchOptions(dict):

    def get(self, name, default=None, use=None):
        try:
            value = self[name]
        except KeyError:
            return default
        else:
            if value:
                if use:
                    try:
                        return use(value)
                    except ValueError:
                        raise OptionError(name=name)
                else:
                    return value
            else:
                return default


def builder(parser):
    # <session>
    def session():
        # <action>
        def action(name):
            options = WatchOptions()
            # <option>
            def option(name):
                options[name] = yield VALUE
            # </option>
            yield option
            parser.result.append((name, options))
        # </action>
        return action
    # </session>
    return session
