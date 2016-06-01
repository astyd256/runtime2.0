# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



import re

class VDOM_hypertext(VDOM_object):

    def render(self, contents=""):
        id = 'o_' + (self.id).replace('-', '_')

        display = u"display:none;" if self.visible == "0" else u"display:block;"

        if self.nostyle == "2":
            if self.visible == "0":
                return "<span style=\"%s\">%s</span>" % (display, self.htmlcode)
            else:
                return "%s" % (self.htmlcode)
        elif self.nostyle == "1":
            return "<span id=\"%s\" style=\"%s\">%s</span>" % (id, display, self.htmlcode)
        else:
            if self.overflow == "1":
                ov = 'hidden'
            elif self.overflow == "2":
                ov = 'scroll'
            elif self.overflow == "3":
                ov = 'visible'
            else:
                ov = 'auto'

            height = u"height: "+self.height+"px;" if int(u"0%s" % self.height) > 0 else u""

            style = u"overflow:"+ov+"; position: absolute; z-index: "+self.zindex+"; top: "+self.top+"px; left: "+self.left+"px; width: "+self.width+"px; "+height

            classname = u'class="%s"' % self.classname if self.classname else u""

            if VDOM_CONFIG_1["DEBUG"] == "1":
                debug_info = u"objtype='hypertext' objname='%s' ver='%s'" % (self.name, self.type.version)
            else:
                debug_info = u""

            return "<div %s id=\"%s\" %s style=\"%s%s\">%s</div>" % (debug_info, id, classname, style, display, self.htmlcode)


    def wysiwyg(self, contents=""):
        from scripting.utils.wysiwyg import get_empty_wysiwyg_value

        if not self.htmlcode:
            image_id = "f74a4262-469b-f3cf-8e10-08a127dfbdbf"

            result = get_empty_wysiwyg_value(self, image_id)

            return VDOM_object.wysiwyg(self, contents=result)

        # get overflow value
        overflow_dict = {"0":"auto", "1":"hidden", "2":"scroll", "3":"visible"}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]

        # disable javascript
        html_with_server = re.sub("=/", "=http://" + request.server.host + "/"  ,self.htmlcode)
        html_wys = re.sub("(href\s*=\s*['\"]{1}(.*?)['\"]{1})", r"""style="text-decoration: underline; color:#394fa2;" """,html_with_server)
        html_wys = re.sub("<script\s*\>", "<pre>Script:<br/>" ,self.htmlcode)
        html_wys = re.sub("</script>", "</pre>" ,self.htmlcode)

        result = \
            u"""<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}"
                        order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                    <htmltext top="0" left="0" width="{width}" height="{height}" locked="true" overflow="{overflow}">
                        {html_data}
                    </htmltext>
                </container>
            """.format( id = self.id,
                        visible = self.visible,
                        zindex = self.zindex,
                        hierarchy = self.hierarchy,
                        order = self.order,
                        top = self.top,
                        left = self.left,
                        width = self.width,
                        height = self.height,
                        html_data = "<![CDATA"+"["+ html_wys +"]"+"]>",
                        overflow = overflow)

        return VDOM_object.wysiwyg(self, contents=result)

    
