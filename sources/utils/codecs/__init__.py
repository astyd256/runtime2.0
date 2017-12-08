
from codecs import register

import html
import url
import xml
import cdata
import js


register(html.search)
register(url.search)
register(xml.search)
register(cdata.search)
register(js.search)
