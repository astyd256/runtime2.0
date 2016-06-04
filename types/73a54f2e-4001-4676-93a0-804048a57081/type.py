
class VDOM_text(VDOM_object):

    def render(self, contents=""):
        font=[
            self.fontstyle if self.fontstyle=="italic" else None,
            self.fontweight if self.fontweight=="bold" else None,
            "%spx" % self.fontsize or "12px",
            "%s" % self.fontfamily.replace('"', "'") or None]

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) <> 0 else u""
        style = {
            "display": "none" if self.visible=="0" else None,
            "position": self.position,
            "overflow": "auto",
            "top": "%spx" % self.top,
            "left": "%spx" % self.left,
            "width": "%spx" % self.width,
            "text-align": self.align or None,
            "font": " ".join(filter(None, font)),
            "color" : "#%s" % self.color if self.color else None,
            "text-decoration": self.textdecoration or None}

        hint = u" title=\"%s\" " % (self.hint).replace('"', '&quot;') if (self.hint).strip() <> "" else u""

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='text' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        result = u"<div %(debug_info)s id=\"%(id)s\" style=\"%(zind)s%(style)s%(css)s\" class=\"%(classname)s\" %(hint)s>%(value)s</div>" % {
            "hint": hint,
            "zind": style_zindex,
            "debug_info": debug_info,
            "id": self.id_special,
            "style": "; ".join(["%s: %s" % (key, value) for key, value in style.iteritems() if value]),
            "css": "; %s" % self.css if self.css else "",
            "classname": self.classname,
            "value": self.value}

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        the_value = self.value

        value = "<![CDATA[%s]""]>" % the_value

        empty_value = \
            u"""<svg>
                <text fill="#cccccc" x="5" y="10">Text</text>
            </svg>""" if the_value == "" else ""

        fontsize="fontsize=\"%s\""%self.fontsize if self.fontsize else ""

        editable="value,color,fontfamily,fontsize,fontstyle,fontweight,align,textdecoration"

        result=\
            u"""<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}" top="{top}" left="{left}" width="{width}">
                {empty_value}
                <text top="{textTop}" left="{textLeft}" width="{width}" color="#{color}" fontstyle="{fontstyle}" fontweight="{fontweight}" fontfamily="{fontfamily}"
                {fontsize} textalign="{align}" textdecoration="{textdecoration}" editable="{editable}">{value}</text>
                {contents}
            </container>""".format(
                id = self.id,
                visible = self.visible,
                zindex = self.zindex,
                hierarchy = self.hierarchy,
                order = self.order,
                top = self.top,
                left = self.left,
                width = self.width,
                textTop = 0,
                textLeft = 0,
                color = self.color,
                fontstyle = self.fontstyle,
                fontweight = self.fontweight,
                fontfamily = self.fontfamily.replace('"', '').replace("'", ''),
                fontsize = fontsize,
                align = self.align,
                textdecoration = self.textdecoration,
                editable = editable,
                value = value,
                contents = contents,
                empty_value = empty_value
            )

        #print result
        return VDOM_object.wysiwyg(self, contents=result)


