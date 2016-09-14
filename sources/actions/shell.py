
import startup
from logs import console
from utils.threads import intercept
from utils.tracing import show_exception_trace


def run():
    """
    enter interactive mode
    """
    intercept(ctrlc=lambda: None)
    parser = startup.manage.parser
    parser.disable(optional_actions=True)

    while True:
        try:
            console.stdout.write("manage > ")
            value = raw_input().strip().lstrip("-")
        except KeyboardInterrupt:
            return
        except EOFError:
            return

        keyword = value.lower()
        if keyword == "help":
            parser.print_help()
        elif keyword == "exit" or keyword == "quit":
            return
        else:
            try:
                arguments = parser.parse_args(value.split())
            except SystemExit:
                pass
            else:
                if arguments.action.run and arguments.action.run is not run:
                    try:
                        arguments.action.run(*arguments.action.arguments)
                    except Exception:
                        show_exception_trace()
                else:
                    parser.print_usage()
