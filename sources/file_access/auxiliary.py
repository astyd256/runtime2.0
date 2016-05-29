
import sys
import re
import os
import os.path
import shutil
import settings


uuid_regex = re.compile(r"[A-F\d]{8}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{4}-[A-F\d]{12}", re.IGNORECASE)


def cleanup_directory(path, ignore_errors=False, onerror=None, remove=False):

    # just to not worry about remove something wrong
    assert uuid_regex.search(path) \
        or path.endswith(settings.RESOURCES_LOCATION) \
        or path.endswith(settings.DATABASES_LOCATION)

    # declare default handlers
    if ignore_errors:
        def onerror(*args):
            pass
    elif onerror is None:
        def onerror(*args):
            raise

    # check for link
    try:
        if os.path.islink(path):
            raise OSError("Cannot clean symbolic link")
    except OSError:
        onerror(os.path.islink, path, sys.exc_info())
        return

    # prepare list
    try:
        names = os.listdir(path)
    except os.error:
        onerror(os.listdir, path, sys.exc_info())
        names = ()

    # remove files and directories
    for name in names:
        fullname = os.path.join(path, name)
        if os.path.isfile(fullname):
            try:
                os.remove(fullname)
            except os.error:
                onerror(os.remove, fullname, sys.exc_info())
        else:
            shutil.rmtree(fullname, ignore_errors, onerror)

    # remove itself if needed
    if remove:
        try:
            os.rmdir(path)
        except os.error:
            onerror(os.rmdir, path, sys.exc_info())
