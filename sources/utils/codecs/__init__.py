
from codecs import register

import html
import url
import xml
import cdata


register(html.search)
register(url.search)
register(xml.search)
register(cdata.search)
