# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request


import json
import re
import sys

from collections import OrderedDict
from uuid import uuid4

import managers
import scripting.utils.wysiwyg as utils_wysiwyg
from memory import vdomxml


# auxiliary

def xml_escape(value):
    global xml_escape

    illegal_unichrs = [
        (0x00, 0x08), (0x0B, 0x1F), (0x7F, 0x84), (0x86, 0x9F),
        (0xD800, 0xDFFF), (0xFDD0, 0xFDDF), (0xFFFE, 0xFFFF),
        (0x1FFFE, 0x1FFFF), (0x2FFFE, 0x2FFFF), (0x3FFFE, 0x3FFFF),
        (0x4FFFE, 0x4FFFF), (0x5FFFE, 0x5FFFF), (0x6FFFE, 0x6FFFF),
        (0x7FFFE, 0x7FFFF), (0x8FFFE, 0x8FFFF), (0x9FFFE, 0x9FFFF),
        (0xAFFFE, 0xAFFFF), (0xBFFFE, 0xBFFFF), (0xCFFFE, 0xCFFFF),
        (0xDFFFE, 0xDFFFF), (0xEFFFE, 0xEFFFF), (0xFFFFE, 0xFFFFF),
        (0x10FFFE, 0x10FFFF)
    ]
    illegal_ranges = ["%s-%s" % (unichr(low), unichr(high))
        for (low, high) in illegal_unichrs if low < sys.maxunicode]
    regex = re.compile(u"[%s]" % u"".join(illegal_ranges))

    def real_xml_escape(text):
        return regex.sub("", text)

    xml_escape = real_xml_escape
    return real_xml_escape(value)


class CachedDict(dict):

    def __init__(self, items, compute):
        super(CachedDict, self).__init__()
        self.initial_items = items
        self.computed_items = {}
        self.compute = compute

    def __getitem__(self, key):
        if key not in self.computed_items:
            self.computed_items[key] = self.compute(self.initial_items[key])

        return self.computed_items[key]


# template

class Template(object):

    __slots__ = ("_attributes", "_vdomxml", "_object")

    def __init__(self, xml, attributes=None):
        self._attributes = attributes or {}
        self._vdomxml = xml
        self._object = vdomxml.loads(xml, managers.engine.application)

    def __getitem__(self, key):
        return self._attributes.get(key.lower(), "")

    def __setitem__(self, key, value):
        self._attributes[key.lower()] = value

    def __delitem__(self, key):
        del self._attributes[key.lower()]

    def render(self, parent):
        if self._attributes:
            cache = {0: (self._object, {})}

            for name, value in self._attributes.iteritems():
                pair = name.rsplit(".", 1)

                if len(pair) == 1:
                    target, attributes = cache[0]
                elif pair[0] in cache:
                    target, attributes = cache[pair[0]]
                else:
                    target, attributes = self._object, {}
                    for object_name in pair[0].split("."):
                        target = target.objects.get(object_name)
                        if not target:
                            break
                    else:
                        cache[pair[0]] = target, attributes

                if target and pair[-1] in target.attributes:
                    attributes[pair[-1]] = value

            for target, attributes in cache.itervalues():
                target.attributes.update(attributes)

        return managers.engine.render(self._object, parent, "vdom")


# layouts

DEFAULT_MARGIN = 17


class Layout(object):

    __slots__ = ("_elements", "_left", "_top", "_width", "_height", "_margin")

    def __init__(self, margin=DEFAULT_MARGIN):
        self._elements = []
        self._left = 0
        self._top = 0
        self._width = 0
        self._height = 0
        self._margin = margin

    def arrange(self, element):
        pass

    def append(self, element):
        self._elements.append(element)
        if not isinstance(element, basestring):
            self.arrange(element)

    def render(self, parent):
        elements = []
        for element in self._elements:
            if isinstance(element, basestring):
                elements.append(element)
            else:
                element["top"] = str(self._top + int(element["top"] or 0))
                element["left"] = str(self._left + int(element["left"] or 0))
                elements.append(element.render(parent))
        return u"".join(elements)


class VerticalLayout(Layout):

    def __init__(self, margin=DEFAULT_MARGIN):
        super(VerticalLayout, self).__init__(margin=margin)

    def arrange(self, element):
        element["left"] = "0"
        element["top"] = str(self._height + 0 if self._elements else self._margin)

        width = int(element["width"] or 0)
        height = int(element["height"] or 0)

        self._width = max(self._width, width)
        self._height += self._margin + height


class HorizontalLayout(Layout):

    def __init__(self, margin=DEFAULT_MARGIN, container=None):
        super(HorizontalLayout, self).__init__(margin=margin)
        self._width = container._height if container else 0

    def arrange(self, element):
        element["left"] = str(self._left + self._width + self._margin)
        element["top"] = str(self._top)

        width = int(element["width"] or 0)
        height = int(element["height"] or 0)

        self._width += self._margin + width
        self._height = max(self._height, height)


# main class

LAYOUTS = (VerticalLayout, HorizontalLayout, VerticalLayout)

CSS_FIRST = u"dov-item-first"
CSS_LAST = u"dov-item-last"
CSS_ODD = u"dov-item-odd"
CSS_ACTIVE = u"dov-item-active"

CLICK_N_SELECT = (
    "click",
    "ctrlclick",
    "dblclick",
    "ctrldblclick",
    "manual",
)

OVERFLOW = {
    "1": "hidden",
    "2": "scroll",
    "3": "visible",
}

LAYOUT = {
    "0": "clear: both",
    "1": "float: left;",
    "default": "width: 100% !important; clear: both;",
}


class DynamicObjectView(VDOM_object):

    def generate_layout(self):

        # parse data
        try:
            data = json.loads(self.data, object_pairs_hook=OrderedDict)
        except:
            if self.data:
                raise Exception("Unable to parse data")
            data = None

        # parse templates
        try:
            templates = json.loads(self.template)
        except Exception:
            if self.template:
                raise Exception("Unable to parse template")
            templates = None

        # parse bindings
        try:
            bindings = json.loads(self.bindings)
        except Exception:
            if self.bindings:
                raise Exception("Unable to parse bindings")
            bindings = None

        # instantiate layout
        layout = LAYOUTS[int(self.layout)]()
        if not (data and templates and bindings):
            return layout

        # obtain xml template root element attributes
        # TODO: optimize this later...
        def get_root_attributes(xml):
            toplvl = xml.split(">", 1)[0]
            if toplvl[-1] == "/":
                toplvl = toplvl[:-1]
            attrs = [attr.split("=", 1) for attr in toplvl.split(" ") if "=" in attr]
            return {key.lower(): value[1: len(value) - 1] for key, value in attrs}

        # initialize templates
        templates = CachedDict(templates, lambda xml: xml.encode("utf8"))
        templates_attributes = CachedDict(templates, get_root_attributes)

        for index, (uuid, item) in enumerate(data.iteritems(), 1):
            template_name = item.get("vdomclass", "default")
            template_attributes = templates_attributes[template_name]

            template = Template(templates[template_name])

            binding = bindings.get(template_name, {})
            for key, value in item.iteritems():
                if key not in binding:
                    continue

                attributes = binding[key]
                if not isinstance(attributes, list):
                    attributes = [attributes]

                for name in attributes:
                    template[name] = xml_escape(value)

            classes = (
                template["classname"],
                template_attributes["classname"],
                CSS_FIRST if index == 1 else None,
                CSS_LAST if index == len(data) else None,
                CSS_ODD if index % 2 == 0 else None,
                CSS_ACTIVE if self.activeitem == uuid else None,
                u"dov-item dov-item-%d" % index
            )

            template["name"] = "dovtemplate_%d" % index
            template["classname"] = u" ".join(filter(None, classes))
            template["dataid"] = uuid

            layout.append(template)

        return layout

    def compile_style(self):
        object_style = u"{display}" \
            "z-index: {zindex};" \
            "position: {position};" \
            "top: {top}px;" \
            "left: {left}px;" \
            "height: {height}px;" \
            "width: {width}px;" \
            "overflow: {overflow};".format(
                display=u"display:none;" if self.visible == "0" else u"",
                zindex=self.zindex,
                position=self.position,
                top=self.top,
                left=self.left,
                width=self.width,
                height=self.height,
                overflow=OVERFLOW.get(self.overflow, "auto"))

        id4js = "o_" + self.id.replace('-', '_')
        element_style = u"<style type=\"text/css\">\n" \
            "{user_css}\n" \
            "#{id4js} .dov-item {{{layout}}}\n" \
            "</style>\n".format(
                id4js=id4js,
                user_css=self.css % {"id": id4js},
                layout=LAYOUT.get(self.layout, "default"))

        return object_style, element_style

    def render(self, contents=""):
        layout = self.generate_layout()
        id4js = "o_" + self.id.replace('-', '_')
        insertmethod = ["insertHTMLAtBegining", "insertHTMLAtEnd"][int(self.insertmethod)]

        if request.render_type == "e2vdom" and self.dynamicrender == "1":
            result = u"""<noreplace/>
<div id="{tmp_id}" style="display:none">{contents}</div>
<script type='text/javascript'>
$(document).ready(function(){{
  var x = $('#{id4js}>div.dov-content');
  var dovtmp = $('#{tmp_id}:last');
  if ($.trim(dovtmp.html()) != '') {{
      $("#{id4js}").dynamicObjectView("{insertmethod}", dovtmp);
  }}
}});
</script>""".format(
                id4js=id4js,
                tmp_id=str(uuid4()),
                contents=layout.render(self),
                insertmethod=insertmethod,
            )

            return VDOM_object.render(self, contents=contents + result)
        else:
            options = {
                "dragndrop": self.draggable == "1",
                "dragnsort": self.sortable == "1",
                "dragndropHelper": self.draghelper if self.draghelper else "clone",
                "dynamicLoading": self.dynamicloading == "1",
                "clickClasses": self.clickclass.strip().split(),
                "clickAndSelect": CLICK_N_SELECT[int(self.selectonclick)],
                "multiSelection": self.selectionmode == "1",
            }

            object_style, element_style = self.compile_style()
            result = u"""{element_style}
<div name="{name}" id="{id4js}" style="{object_style}" class="{classes}">
<div class='dov-content'>
{contents}
<span class='dov-eoi' style='display:block;clear:both'></span>
</div>
</div>
<script>jQuery(document).ready(function(){{jQuery("#{id4js}").dynamicObjectView({options});}});</script>"""
            contents += result.format(
                name=self.name,
                element_style=element_style,
                id4js=id4js,
                object_style=object_style,
                classes=self.classname,
                contents=layout.render(self),
                options=json.dumps(options)
            )

            return VDOM_object.render(self, contents=contents)

    def wysiwyg(self, contents=""):
        image_id = "76bfc7be-dbe3-46e3-8d11-cc78a576b63a"
        result = utils_wysiwyg.get_empty_wysiwyg_value(self, image_id)
        return VDOM_object.wysiwyg(self, contents=result)
