
from utils.parsing import VALUE


def builder(parser):
    # <session>
    def session():
        # <action>
        def action(name):
            options = {}
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
