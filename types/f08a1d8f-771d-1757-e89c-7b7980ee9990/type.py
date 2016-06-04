
class VDOM_editableresource(VDOM_object):

    def render(self, contents=""):
        if self.visible == "1":
            resource = application.resources.get_by_label(self.id, "userdata")
            if resource:
                res_id = resource.id
            else:
                res_type = "js" if self.datatype == '1' else "css" if self.datatype == '2' else "txt"
                res_id = application.resources.create_temporary(self.id, "data", self.data, res_type, "data")

            udata = ""
            if self.datatype == "1":
                if res_id:
                    udata = u'<script type="text/javascript" src="/%s.res"></script>' % res_id
                    request.dyn_libraries[self.name] = udata
                    # return ""
                    return VDOM_object.render(self, contents="")
                else:
                    udata = '<!-- no res for script -->'
            elif self.datatype == "2":
                # first line of the css must be: @charset "UTF-8";
                if res_id:
                    udata = u'<style rel="stylesheet" type="text/css">@import url("/%s.css");</style>' % res_id
                    request.dyn_libraries[self.name] = udata
                    # return ""
                    return VDOM_object.render(self, contents="")
                else:
                    udata = '<!-- no res for style -->'
            else:
                udata = self.data

            id = 'o_' + (self.id).replace('-', '_')
            if self.nostyle == "2":
                # return u"%s" % udata
                return VDOM_object.render(self, contents=u"%s" % udata)
            elif self.nostyle == "1":
                # return u"<span id=\"%(id)s\">%(data)s</span>" % { "id": id, "data": udata }
                return VDOM_object.render(self, contents=u"<span id=\"%(id)s\">%(data)s</span>" % { "id": id, "data": udata })
            else:
                if self.overflow == "1":
                    ov = 'hidden'
                elif self.overflow == "2":
                    ov = 'scroll'
                elif self.overflow == "3":
                    ov = 'visible'
                else:
                    ov = 'auto'
                style = "overflow:"+ov+"; position: absolute; z-index: "+self.zindex+"; top: "+self.top+"px; left: "+self.left+"px; width: "+self.width+"px; height: "+self.height+"px"
                # return u"<div id=\"%(id)s\" style=\"%(style)s\">%(data)s</div>" % { "id":id, "style":style, "data":udata }
                return VDOM_object.render(self, contents=u"<div id=\"%(id)s\" style=\"%(style)s\">%(data)s</div>" % { "id":id, "style":style, "data":udata })
        else:
            # return ""
            return VDOM_object.render(self, contents="")
            
    def get_data_format (self) :
        format_dict = {"1":"JS", "2":"CSS"}

        text_format = ""
        try:
            text_format = format_dict[self.datatype] if self.datatype in format_dict else ""
        except: pass

        return text_format
       
    def wysiwyg(self, contents=""):
        self.width = "50"
        self.height = "50"

        image_width = image_height = 50
        image_x = image_y = 0

        image_id = "a61a9853-638a-8f83-0a70-16a8c65eb8a1"

        text_format = self.get_data_format()

        result = \
            u"""<container id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
                    width="{width}" height="{height}" backgroundcolor="#f0f0f0" alpha="0.5">
                    <svg>
                        <image x="{image_x}" y="{image_y}" href="#Res({image_id})" width="{image_width}" height="{image_height}"/>
                    </svg>
                    <text top="30" left="3" width="{text_width}" textalign="right" color="#ffffff">{text_format}</text>
                </container>
            """.format(
                    id = self.id,
                    zindex = self.zindex, hierarchy = self.hierarchy,
                    top = self.top, left = self.left,
                    width = self.width, height = self.height,
                    image_x = image_x, image_y = image_y,
                    image_id = image_id, text_format = text_format,
                    image_width = image_width, image_height = image_height,
                    text_width = image_width-6)

        return VDOM_object.wysiwyg(self, contents=result)
            
