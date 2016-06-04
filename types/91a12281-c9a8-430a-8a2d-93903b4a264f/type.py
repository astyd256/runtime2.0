
import sys


class VDOM_bar(VDOM_object):

    def render(self, contents=""):
        display = u"display:none;" if self.visible == "0" else u""

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) <> 0 else u"" # 123

        classname = u'class="%s"' % self.classname if self.classname else u""

        style = (u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px;"""
             u"""width: {width}px; height: {height}px; background: #{color}""")\
            .format(
                display = display, zind = style_zindex, pos = self.position,
                top = self.top, left = self.left,
                width = self.width, height = self.height, color = self.color)

        id = u"o_" + (self.id).replace('-', '_')

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='bar' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        result = u"""<div {debug_info} id="{id}" style="{style}" {classname}>{contents}</div>""".format(
            debug_info = debug_info,
            id = id,
            style = style,
            classname = classname,
            contents = contents )

        return VDOM_object.render(self, contents=result)


    def wysiwyg(self, contents=""):

        result = \
            u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="#{color}"/>
                    </svg>
                    {contents}
                </container>
            """.format(
                    id = self.id, vis = self.visible, zind = self.zindex,
                    hierarchy = self.hierarchy, order = self.order,
                    top = self.top, left = self.left, width = self.width, height = self.height,
                    color = self.color, contents = contents)

        return VDOM_object.wysiwyg(self, contents=result)
