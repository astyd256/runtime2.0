# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request

from scripting import e2vdom, utils

class VDOM_container(VDOM_object):

    def render(self, contents=""):

        if self.securitycode:
            self.visible = "0"
            if session["SecurityCode"] and str(session["SecurityCode"]) in self.securitycode.split(";"):
                self.visible = "1"

        display = u" display:none; " if self.visible == "0" else u""

        e2vdom.process(self)
        
        if self.overflow == "1":
            overflow = u"hidden"
        elif self.overflow == "2":
            overflow = u"scroll"
        elif self.overflow == "3":
            overflow = u"visible"
        else:
            overflow = u"auto"

        height = u"height: %spx;" % self.height if self.heightauto == "0" else u""

        background_color = u"background-color: #%s;" % self.backgroundcolor if self.backgroundcolor != "" else u""

        background_image = u"background-image: url('%s');" % utils.id.id2link1(self.backgroundimage) if self.backgroundimage != "" else u""

        if self.backgroundrepeat == '1':
            background_repeat = 'background-repeat:no-repeat;'
        elif self.backgroundrepeat == '2':
            background_repeat = 'background-repeat:repeat-x;'
        elif self.backgroundrepeat == '3':
            background_repeat = 'background-repeat:repeat-y;'
        else:
            background_repeat = u''

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) <> 0 else u""

        style = u"""{display} {zind} position: {pos}; top: {top}px; left: {left}px;
                    width: {width}px; overflow: {overflow}; {height} {background_color} {background_image} {background_repeat}"""\
                .format(display = display, zind = style_zindex, pos = self.position,
                    background_color = background_color, background_image = background_image, background_repeat = background_repeat,
                    top = self.top, left = self.left, width = self.width, overflow = overflow, height = height)

        id = u"o_" + (self.id).replace('-', '_')
        footer = u"""rel="footer" """ if self.footer == "1" else u""
        classname = u"""class="%s" """ % self.classname if self.classname else u""

        if self.titlewrap == "0":
            title_tag = u""
            cont_tag = u"%s" % contents
        else:
            title_tag = u"""<div class="title"><div><h{twrap}>{title}</h{twrap}></div></div>"""\
                        .format(twrap = self.titlewrap, title = self.title)
            cont_tag = u"""<div class="content">%s</div>""" % contents


        debug_info = u""
        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='container' objname='%s'" % ( self.name )


        result = u"""<div {debug_info} {footer} id="{id}" style="{style}" {classname}>{title_tag}{cont_tag}</div>"""\
                .format(debug_info = debug_info, footer =  footer, id = id, style = style, classname = classname,
                            title_tag = title_tag, cont_tag = cont_tag)

        return VDOM_object.render(self, contents=result)




    def wysiwyg(self, contents=""):
        import utils.wysiwyg

        colorNumber = self.backgroundcolor if self.backgroundcolor != "" else self.designcolor
        colorValue = "#" + colorNumber if colorNumber != "" else "none"

        # title
        title_text = ""
        if self.title!="" and self.titlewrap!="0":
            title_text = u"""<text x="5" y="14" fill="#000000" font-size="14" width="{width}">{title}</text>
                                """.format(title = self.title, width=self.width)

        # show icon if container is empty
        empty_container_image = ""
        if len(contents)==0 and self.backgroundimage == "":
            image_id = "8c8c753c-f1e4-07bb-e5bf-08771d63f502"
            image_width = image_height = 50

            image_x, image_y, image_width, image_height = utils.wysiwyg.get_centered_image_metrics( image_width, image_height, int(self.width), int(self.height) )

            empty_container_image = u"""<image href="#Res({image_id})" x="{image_x}" y="{image_y}"
                                                        width="{image_width}" height="{image_height}" />
                                        """.format(image_id = image_id, image_width = image_width,
                                         image_height = image_height, image_x = image_x, image_y = image_y)

        bg_image = ""
        if self.backgroundimage != "":
            if self.backgroundrepeat == '0':
                bg_image_repeat = 'repeat'
            elif self.backgroundrepeat == '1':
                bg_image_repeat = 'no-repeat'
            elif self.backgroundrepeat == '2':
                bg_image_repeat = 'repeat-x'
            elif self.backgroundrepeat == '3':
                bg_image_repeat = 'repeat-y'
            else:
                bg_image_repeat = u''

            bg_image = \
                u"""<image href="#Res({backgroundimage})" x="0" y="0" repeat="{repeat}" containerWidth="{containerWidth}"
                        containerHeight="{containerHeight}" />
                """.format(
                    backgroundimage = self.backgroundimage, repeat = bg_image_repeat,
                    containerWidth = self.width,  containerHeight = self.height
                )

        # get overflow value
        overflow_dict = {"0":"auto", "1":"hidden", "2":"scroll", "3":"visible"}
        overflow_num = self.overflow if self.overflow else "0"
        overflow = overflow_dict[overflow_num]
        
        result = \
            u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}" overflow="{overflow}">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="{colorValue}"/>
                        {empty_container_image}
                        {bg_image}
                        {title_text}
                    </svg>{contents}
                </container>""".format(
                    id = self.id, vis = self.visible, zind = self.zindex,
                    hierarchy = self.hierarchy, order = self.order, colorValue = colorValue,
                    top = self.top, left = self.left, width = self.width, height = self.height,
                    contents = contents,
                    title_text = title_text,
                    empty_container_image = empty_container_image,
                    bg_image = bg_image,
                    overflow = overflow
                )

        return VDOM_object.wysiwyg(self, contents=result)


# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # object = application.objects.search(object_id)

    if object.parent and object.parent.type.class_name == "VDOM_tabview" and object.attributes.lockposition == "1" and int(object.attributes.top) != 20 and int(object.attributes.left) != 1:
        top_container = 20
        left_container = 1
        # object.set_attributes({"left": left_container, "top": top_container})
        object.attributes.update(left=left_container, top=top_container)

    return ""
