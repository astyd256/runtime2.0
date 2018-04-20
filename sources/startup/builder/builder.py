
import sys
import os.path
import re

from distutils.command.build_ext import build_ext
from setuptools import setup

import settings

from utils.output import section, show, warn
from .buffer import OutputBuffer


SETUP_SCRIPT = """
setup(name="runtime",
    cmdclass={"build_ext": BuildExtension},
    ext_modules=extensions,
    options={
        "build_ext": {"build_lib": temporary, "build_temp": temporary},
        "clean": {"build_lib": temporary, "build_temp": temporary}
    })
"""


class BuildExtension(build_ext):

    def build_extensions(self):

        def apply_options(**options):
            options = options.get(self.compiler.compiler_type)
            if options:
                if isinstance(options, list):
                    compiler_options, linker_options = options, None
                elif isinstance(options, tuple):
                    compiler_options, linker_options = options
                for extension in self.extensions:
                    if compiler_options:
                        extension.extra_compile_args = compiler_options
                    if linker_options:
                        extension.extra_link_args = linker_options

        if settings.TREAT_WARNINGS_AS_ERRORS:
            apply_options(msvc=["/WX"], unix=["-Werror"])

        build_ext.build_extensions(self)


class Builder(object):

    def __init__(self, **keywords):
        self._temporary = os.path.join(settings.TEMPORARY_LOCATION, "builder")
        self._extensions = keywords

    def build(self, *arguments):

        def build_extension(extension):
            arguments_backup = sys.argv[:]
            try:
                sys.argv = "setup.py", "build_ext", "--inplace", "clean"
                with output_buffer:
                    exec(SETUP_SCRIPT, {
                        "BuildExtension": BuildExtension,
                        "temporary": self._temporary,
                        "setup": setup,
                        "extensions": [extension]}, {})
            except BaseException as error:
                show("")
                warn(re.sub(r"^(error:\s)?", "", str(error), flags=re.IGNORECASE))
                for line in output_buffer.lines:
                    warn(line,
                        indent=settings.LOGGING_INDENT,
                        continuation=settings.LOGGING_INDENT)
                raise
            finally:
                sys.argv = arguments_backup

        try:
            output_buffer = OutputBuffer()
            with section("build extensions"):
                if arguments:
                    for name in arguments:
                        extension = self._extensions.get(name)
                        if not extension:
                            warn("extension \"%s\" not found" % name)
                            return False
                        show("build %s extension" % extension.name)
                        build_extension(extension)
                else:
                    for extension in self._extensions.itervalues():
                        show("build %s extension" % extension.name)
                        build_extension(extension)
        except BaseException:
            return False
        else:
            return True
