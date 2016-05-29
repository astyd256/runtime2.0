
# coding=utf8

import json
from collections import OrderedDict
from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request
from scripting.utils import get_empty_wysiwyg_value


class DynamicObjectView(VDOM_object):

    def render(self, contents=""):

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

        from scripting.utils.vdomxml import load_as_template
        template = load_as_template(templates["default"])

        print template

        return VDOM_object.render(self, contents=contents)

    def wysiwyg(self, contents=""):
        result = get_empty_wysiwyg_value(self, "76bfc7be-dbe3-46e3-8d11-cc78a576b63a")
        return VDOM_object.wysiwyg(self, contents=result)
