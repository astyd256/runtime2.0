# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request


import managers
from scripting import e2vdom
import scripting.utils.wysiwyg as utils_wysiwyg
from memory import vdomxml, vdomjson


WYSIWYG_IMAGE_UUID = "76bfc87a-dbe3-46e3-8d11-cc78a576b63a"


class VDOM_DynamicObject(VDOM_object):

    def inner_render(self):
        e2vdom.process(self)
        try:
            try:
                root = vdomxml.loads(self.vdomxml.encode("utf8"), managers.engine.application)
            except:
                if self.vdomxml.strip():
                    raise
                else:
                    return ""
            try:
                vdomjson.loads(self.vdomactions, root, self._origin)
            except:
                if self.vdomactions.strip():
                    raise
            with e2vdom.select(dynamic=True):
                instance = root.factory(self.context)(self)
                e2vdom.update(types=instance._types)
                return instance.render()
        except Exception as error:
            if self.debugmode == "1":
                raise
            else:
                message = self.rendererrormsg or u"Render error: %s" % error
                return u"<span class=\"render-error\">%s</span>" % message

    # use inner_render for raw_content
    def render(self, contents=""):
        dynamic_contents = self.inner_render()
        style = u"{display}z-index: {zindex}; position: {pos}; " \
            "top: {top}px; left: {left}px; height: {height}px; width: {width}px; " \
            "overflow: {overflow};".format(
                display=u"display:none; " if self.visible == "0" else u"",
                zindex=self.zindex,
                pos=self.position,
                top=self.top,
                left=self.left,
                width=self.width,
                height=self.height,
                overflow={"1": "hidden", "2": "scroll", "3": "visible"}.get(self.overflow, "auto"))
        contents += u"""<div name="{name}" id="{id}" style="{style}" class="{classes}">{contents}</div>""".format(
            name=self.name,
            id=u"o_" + self.id.replace('-', '_'),
            style=style,
            classes=self.classname,
            contents=dynamic_contents)
        return super(VDOM_DynamicObject, self).render(contents=contents)

    def wysiwyg(self, contents=""):
        contents += utils_wysiwyg.get_empty_wysiwyg_value(self, WYSIWYG_IMAGE_UUID)
        return super(VDOM_DynamicObject, self).wysiwyg(contents=contents)
