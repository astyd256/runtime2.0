
import re


patterns = {
    "vscript": (
        re.compile("(?:^\s*[Rr][Ee][Mm].+$)|(?:'.+$)|(?:\"[^\"]*\")", re.MULTILINE),
        re.compile("(?<![_0-9A-Za-z])this(\.\s*[_A-Za-z][_0-9A-Za-z]*)+")
    ),
    "python": (
        re.compile(
            "(?:#.+$)|(?:[uU]?[rR]?(?:"
            r"'''(?:[^']|\\'|'{1,2}(?!'))*'''|'(?:[^'\n]|\\')*'(?!')|"
            r'"""(?:[^"]|\\"|"{1,2}(?!"))*"""|"(?:[^"\n]|\\")*"(?!"))'
            ")", re.MULTILINE),
        re.compile("(?<![_0-9A-Za-z])self(\.[_A-Za-z][_0-9A-Za-z]*)+")
    )
}


def analyze_script_structure(source, language, names=None):
    try:
        language_patterns = patterns[language]
    except KeyError:
        return {}  # empty for unknown

    # remove commentaries and strings
    source = language_patterns[0].sub("\01", source)

    # search names in the remaining
    names = names or {}
    for match in language_patterns[1].finditer(source):
        this = names
        for name in match.group().lower().split(".")[1:]:
            name = name.strip()
            if this is None:
                this = {name: None}
                last[last_name] = this  # noqa
                last = this
                last_name = name
                this = None
            elif name in this:
                last = this
                last_name = name
                this = this[name]
            else:
                this[name] = None
                last = this  # noqa
                last_name = name  # noqa
                this = None

    return names
