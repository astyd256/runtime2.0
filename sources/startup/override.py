
import os.path
import json

from StringIO import StringIO
from ConfigParser import SafeConfigParser

import settings


DEFAULT_SECTION = "NONAME"
EXTRA_SECTIONS = "SERVER", "MANAGE", "WINDOWS", "LINUX", "FREEBSD"
MISSING = "MISSING"


def override(filename):
    if not os.path.isfile(filename):
        print "File to override settings not found: %s" % filename
        return

    filelike = StringIO()
    filelike.write("[%s]\n" % DEFAULT_SECTION)

    with open(filename, "r") as file:
        filelike.write(file.read())

    filelike.seek(0)

    config = SafeConfigParser()
    config.readfp(filelike)

    def override_from_section(section):
        if not config.has_section(section):
            return

        for name, value in config.items(section):
            settings_name = name.replace("-", "_").upper()

            if settings_name.startswith("_"):
                print "Ignore unsupported option: %s" % name
                continue

            current_value = getattr(settings, settings_name, MISSING)
            if current_value is MISSING:
                print "Ignore unknown option: %s" % name
                continue

            try:
                if value == "None":
                    setattr(settings, settings_name, None)
                elif isinstance(current_value, bool):
                    setattr(settings, settings_name, bool(value))
                elif isinstance(current_value, int):
                    setattr(settings, settings_name, int(value))
                elif isinstance(current_value, float):
                    setattr(settings, settings_name, float(value))
                elif isinstance(current_value, basestring):
                    setattr(settings, settings_name, str(value))
                elif isinstance(current_value, dict):
                    setattr(settings, settings_name, json.loads(value))
                else:
                    for caster in (int, float, json.loads):
                        try:
                            value = caster(value)
                            break
                        except Exception:
                            continue
                    setattr(settings, settings_name, value)
            except Exception as error:
                print "Unable to parse option %s: %s" % (name, error)

    override_from_section(DEFAULT_SECTION)
    for name in EXTRA_SECTIONS:
        if getattr(settings, name):
            override_from_section(name)
