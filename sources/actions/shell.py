
import startup # import manage # import arguments
from logs import console
from utils.threads import intercept
from utils.tracing import show_exception_trace


def run():
    """
    enter interactive mode
    """
    intercept(ctrlc=lambda: None)
    parser = startup.manage.parser
    while True:
        try:
            console.stdout.write("manage > ")
            value = raw_input()
        except KeyboardInterrupt:
            return
        except EOFError:
            return

        try:
            arguments = parser.parse_args(value.split())
        except SystemExit:
            pass
        else:
            if arguments.action.name:
                try:
                    arguments.action.run(*arguments.action.arguments)
                except Exception:
                    show_exception_trace()
            else:
                parser.print_usage()
