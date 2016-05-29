
import ast
from cStringIO import StringIO


def wrapfilelike(function):
    def wrapper(*arguments, **keywords):
        filelike = keywords.get("filelike")
        if not filelike:
            keywords["filelike"] = filelike = StringIO()
            function(*arguments, **keywords)
            return filelike.getvalue()
    return wrapper


def source_is_empty(source):
    tree = ast.parse(source, mode="exec")
    iterator = ast.walk(tree)
    try:
        iterator.next()
        iterator.next()
        return False
    except StopIteration:
        return True
