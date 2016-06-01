# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



from scripting import utils

class VDOM_image(VDOM_object):

    def render(self, contents=""):

        if self.value:
            link = utils.id.id2link1(self.value)
        elif self.externalurl:
            link = self.externalurl
        elif self.base64stream:
            import base64
            data = base64.b64decode(self.base64stream)
            res_id = application.resources.create_temporary(self.id, "data", data, "png", "data")
            link = "/%s.png"%res_id
        else:
            link = ""

        visible = u"display:none;" if self.visible == "0" else ""

        style = u"z-index: {zindex}; position: {position}; top: {top}px; left: {left}px".format(
            zindex = self.zindex,
            position = self.position,
            top = self.top,
            left = self.left)
        id = 'o_' + (self.id).replace('-', '_')
        title = iw = ih = ""
        if self.hint:
            title = u"""title="{hint}" """.format(hint = self.hint)
        if self.width == "":
            self.width = 0
        if int(self.width) > 0:
            iw = u"""width="{width}" """.format(width = self.width)
        if self.height == "":
            self.height = 0
        if int(self.height) > 0:
            ih = u"""height="{height}" """.format(height = self.height)

        result = \
            u"""<div id="{id}" style=" {visible} {style}">
                    <img src="{link}" {width} {height} tabindex="{tabindex}" {title} />
                </div>
            """.format(
                    id = id,
                    visible = visible,
                    style = style,
                    link = link,
                    width = iw,
                    height = ih,
                    tabindex = self.tabindex,
                    title = title)

        return VDOM_object.render(self, contents=result)

    def is_correct_exturnal_url (self, url) :
        if url.lower().startswith("http://") or url.lower().startswith("https://"):
            return True
        return False

    def wysiwyg(self, contents=""):
        from scripting.utils.wysiwyg import get_empty_wysiwyg_value

        if self.value:      # show image from resources
            editable = u' editable="value" '

            result = \
                u"""<container id="{id}" zindex="{zindex}" hierarchy="{hierarchy}" top="{top}" left="{left}"
                        width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000">
                        <svg>
                            <image x="{image_x}" y="{image_y}" href="#Res({image_id})"
                                width="{width}" height="{height}" {editable}/>
                        </svg>
                    </container>
                """.format(
                        id = self.id,
                        zindex = self.zindex,
                        hierarchy = self.hierarchy,
                        top = self.top,
                        left = self.left,
                        width = self.width or 50,
                        height = self.height or 50,
                        image_x = 0,
                        image_y = 0,
                        image_id = self.value,
                        editable = editable)

        elif self.externalurl:
            url = self.externalurl
            if not self.is_correct_exturnal_url(self.externalurl):
                url = u"http://empty.png"

            result = \
                u"""<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}"
                        order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
                        <htmltext top="0" left="0" width="{width}" height="{height}" locked="true">
                            <img width="{width}" height="{height}" src="{image_url}"/>
                        </htmltext>
                    </container>
                """.format(
                        id = self.id,
                        visible = self.visible,
                        zindex = self.zindex,
                        hierarchy = self.hierarchy,
                        order = self.order,
                        top = self.top,
                        left = self.left,
                        width = self.width or 50,
                        height = self.height or 50,
                        image_url = url)

        else:
            image_id = "e8115c4a-903a-a4c6-c0bc-08a336586d51"
            result = get_empty_wysiwyg_value(self, image_id)

        return VDOM_object.wysiwyg(self, contents=result)

# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # o = application.objects.search(object_id)
    o = object

    # if "value" in param and not "width" in param and not "height" in param:
    if "value" in attributes and not "width" in attributes and not "height" in attributes:
        # attr = param["value"]
        attr = attributes["value"]
        # res_id = attr["value"]
        res_id = attributes["value"]

        ro = application.resources.get(res_id)
        if not ro:
            return "Resource not found"

        # get image resource, obtain width and height and set width and height of the object
        from PIL import Image
        import cStringIO
        s = cStringIO.StringIO()
        s.write(ro.get_data())
        s.seek(0, 0)
        im = Image.open(s)
        width, height = im.size
        # set attributes
        if o.attributes.width != width or o.attributes.height != height:
            # o.set_attributes({"width": width, "height": height})
            o.attributes.update(width=width, height=height)
    else:
        # if "width" in param and param["width"]["value"] != '' and int(param["width"]["value"]) > 2500:
        #     o.set_attributes({"width": 2500})
        if "width" in attributes and attributes["width"] != '' and int(attributes["width"]) > 2500:
            o.attributes.update(width=2500)
        # if "height" in param and param["height"]["value"] != '' and int(param["height"]["value"]) > 2500:
        #     o.set_attributes({"height": 2500})
        if "height" in attributes and attributes["height"] != '' and int(attributes["height"]) > 2500:
            o.attributes.update(height=2500)
    return ""

        
