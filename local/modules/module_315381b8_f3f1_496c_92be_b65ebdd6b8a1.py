# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request


from scripting import utils
import StringIO


class VDOM_button(VDOM_object):

    def compute(self):
        VDOM_object.compute(self)
        self.finalimage = self.image
        self.finalrollover = self.rollover
        self.finaldisabledimg = self.disabledimg
        if self.text:
            if self.image or self.rollover or self.disabledimg:
                try:
                    from scripting.utils.imaging import VDOM_imaging
                    im = VDOM_imaging()
                    im.create_font(name = self.fontfamily, size = int(self.fontsize), 
                            fontstyle = self.fontstyle, fontweight = self.fontweight)
                    if self.image:
                        resource = application.resources.get_by_label(self.id, "image")
                        if resource:
                            self.finalimage = resource.id
                        else:
                            im.load(application.id, self.image)
                            im.write_text(self.text,
                                color = ( int(self.color[:2], 16), int(self.color[2:4], 16), int(self.color[4:6], 16)),
                                align = self.align, ident = self.fontshift, textdecoration = self.textdecoration)
                            self.finalimage = im.save_temporary(application.id, self.id, "image")
                    if self.rollover:
                        resource = application.resources.get_by_label(self.id, "rollover")
                        if resource:
                            self.finalrollover = resource.id
                        else:
                            im.load(application.id, self.rollover)
                            im.write_text(self.text,
                                color = ( int(self.color[:2], 16), int(self.color[2:4], 16), int(self.color[4:6], 16)),
                                align = self.align, ident = self.fontshift, textdecoration = self.textdecoration)
                            self.finalrollover = im.save_temporary(application.id, self.id, "rollover")
                except Exception as e:
                    debug("Error while text rendering on button image: %s"%str(e))
        if self.image or self.rollover or self.disabledimg:
            self.finaltext = ''
        else:
            self.finaltext = self.text

    def get_anchor(self, link):
        if self.ispressed == "0":
            bgimg = u"background:url('%s');" % utils.id.id2link1(self.finalimage) if self.image and self.rollover else u""
        else:
            bgimg = u"background:url('%s');" % utils.id.id2link1(self.finalrollover) if self.image and self.rollover else u""
        height = u"height:%spx;" % self.height if self.height else u""
        #clname = u"""class="%s" """ % self.classname if self.classname else u""
        if self.disabled == "1":
            clname = u"""class="%s disabled" """ % self.classname
            donot = u""" onclick='return false' """
        else:
            clname = u"""class="%s" """ % self.classname if self.classname else u""
            donot = u""

        return u"""<a style="display:block;text-decoration:none;{height} {bgimage}" href="{link}" title="{hint}" {classname} {donot} {tabindex}>
                """.format(
                        tabindex = "" if int(self.tabindex) <= 0 else u'tabindex="%s"' % self.tabindex,
                        bgimage = bgimg, height = height, link = link,
                        hint = (self.hint).replace('"', '&quot;'),
                        classname = clname, donot = donot)


    def render(self, contents=""):
        id_out = u"o_%s" % (self.id).replace('-', '_')
        styleblock = u""
        scriptblock = u""

        if self.disabled == "0":
            disabled_html = u""
        else:
            zindex_disabled = u"z-index:%s;" % str(int(self.zindex) + 1)
            disabled_html = u"""<div id='{id}_e2vdomhelper' class='disabled-over' style='{zindex_disabled}background:#fff;opacity:0.01;filter:alpha(opacity=1);position:absolute;left:{left}px;top:{top}px;width:{width}px;height:{height}px;'></div>
                """.format(id = id_out, zindex_disabled = zindex_disabled, width = self.width, height = self.height, left = self.left, top = self.top)

        overcss = u"<style>\n" + self.style % {"id": id_out} + u"</style>" if self.style else u""
        disablecss = u""
        representation = u""
        if self.image:
            if self.rollover:
                rover_link = utils.id.id2link1(self.finalrollover)
                overcss =  u"""<style>#%(id)s a:hover {background-image:url("%(image)s")!important}</style>
                                <div style="display:none"><img src="%(image)s" /></div>
                            """ % {"id": id_out, "image": rover_link}
            else:
                hover_link = utils.id.id2link1(self.finalimage)
                if self.ishover == "0":
                    representation = \
                        u"""<img src="{image}" width={width} height={height} 
                                style="text-decoration:none;border:0" title="{hint}" />
                        """.format(image = hover_link, width = self.width, height = self.height, hint = self.hint)
                else:
                    if not self.classname:
                        self.classname = "button"
                    classtut = self.classname
                    if self.ispressed == "1":
                        self.classname = "{classname} {classname}_sel".format(classname = self.classname)

                    # shift background position for show another state of button
                    bgpos_left = str(int(self.height)+int(self.height))

                    styleblock = \
                        u"""<style>.%(classname)s,.%(classname)s_sel
                                {display:block;width:%(width)spx;height:%(height)spx;background:url("%(image)s") left top no-repeat;}
                                .%(classname)s:hover{background-position:left -%(height)spx}
                                .%(classname)s_sel,.%(classname)s_sel:hover{background-position:left -%(bgleft)spx!important}
                            </style>
                        """ % {"classname": classtut, "width": self.width, "height": self.height,
                                    "image": hover_link, "bgleft": bgpos_left}

                    scriptblock += \
                        u"""$q("#%(id)s a").click(function(){$q(this).toggleClass("%(classname)s_sel");});
                        """ % {"id": id_out, "classname": self.classname}
                    #------------------------
            if self.disabledimg:
                disablecss =  u"""<style>#%(id)s .disabled {background-image:url("%(image)s")!important}</style>
                                <div style="display:none"><img src="%(image)s" /></div>
                            """ % {"id": id_out, "image": utils.id.id2link1(self.finaldisabledimg)}
        else:
            spstyle = StringIO.StringIO()
            spstyle.write(u"font: ")
            if self.fontweight == "bold":
                spstyle.write(u"bold ")
            if self.fontstyle == "italic":
                spstyle.write(u"italic ")
            if self.fontsize:
                spstyle.write(u"%spx " % self.fontsize)
            else:
                spstyle.write(u"12px ")
            if self.fontfamily:
                spstyle.write(u"%s" % self.fontfamily.replace('"', "'"))
            spstyle.write(u";")
            if self.align:
                spstyle.write(u"text-align: %s;" % self.align)
            if self.color:
                spstyle.write(u"color: #%s;" % self.color)
            if self.textdecoration:
                spstyle.write(u"text-decoration: %s;" % self.textdecoration)
            
            if not self.style:
                representation = u"""<span style="{style}">{text}</span>""".format(style = spstyle.getvalue(), text = self.text)
            else:
                representation = u"""<span>{text}</span>""".format(text = self.text)
            spstyle.close()

        if not self.text and not self.image and not self.style:
            def_image_id = u"e6017485-3493-484c-6a86-0867a82288fe"
            
            representation = \
                u"""<img src="/{image}.res" width={width} height={height} style="text-decoration:none;border:0" title="{hint}" />
                """.format(
                        image = def_image_id, width = self.width, 
                        height = self.height, hint = self.hint)
        
        width_style = u"width:%spx;" % self.width if self.width else u""
        height_style = u"height:%spx;" % self.height if self.height else u""

        style_zindex = u"z-index:%s;" % self.zindex if int(self.zindex) <> 0 else u""

        style = u"""overflow:hidden;position:absolute;{zindex}left:{left}px;top:{top}px;
                    {wstyle}{hstyle}text-align:{align};border:{border}px solid black;
                """.format(
                        zindex = style_zindex, left = self.left, top = self.top, 
                        wstyle = width_style, hstyle = height_style, align = self.align, border = self.border)

        display = u" display:none; " if self.visible == "0" else u""

        if self.link:
            anchor = self.get_anchor(self.link)
        elif self.containerlink:
            ref_obj = application.objects.search(self.containerlink)
            ref_page = ref_obj.name + ".vdom" if ref_obj else ""
            anchor = self.get_anchor(ref_page)
        else:
            anchor = self.get_anchor(u"javascript://")

        if scriptblock <> '':
            scriptblock = u'<script type="text/javascript">%s</script>' % scriptblock

        if VDOM_CONFIG_1["DEBUG"] == "1":
            debug_info = u"objtype='button' objname='%s' ver='%s'" % (self.name, self.type.version)
        else:
            debug_info = u""

        return u"""{ocss}
                    <div {debug_info} id="{id}" style="{style}{disp}">
                        {anchor}{repr}</a>
                    </div>{disabled}{styleblk}{scriptblk}{disablecss}
                """.format(
                        #tabind = "" if int(self.tabindex) <= 0 else u'tabindex="%s"' % self.tabindex,
                        #tabind = u'tabindex="%s"' % self.tabindex,
                        repr = representation,
                        debug_info = debug_info, ocss = overcss, id = id_out,
                        style = style, disp = display,
                        anchor = anchor,
                        disabled = disabled_html,
                        styleblk = styleblock, scriptblk = scriptblock, disablecss = disablecss)
        
        
    def wysiwyg(self, contents=""):
        if self.border and self.border != "0":
            bw = int(self.border)
            minsize = min(int(self.width), int(self.height))
            if (bw > minsize / 2):
                bw = minsize / 2
            border_string = u""" stroke="#000000" stroke-width="%s" """ % bw
        else:
            bw = 0
            border_string = u""
            
        if not self.text and not self.image:
            image_id = u"e6017485-3493-484c-6a86-0867a82288fe"
            
            outer_width = int(self.width)
            outer_height = int(self.height)
            
            result = \
                u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                        top="{top}" left="{left}" width="{out_wid}" height="{out_hei}">
                        <svg>
                            <image href="#Res({img_id})" x="0" y="0" width="{out_wid}" height="{out_hei}"/>
                        </svg>
                        {contents}
                    </container>
                """.format(
                        id = self.id, vis = self.visible, zind = self.zindex,
                        hierarchy = self.hierarchy, order = self.order,
                        top = self.top, left = self.left, out_wid = outer_width, out_hei = outer_height,
                        img_id = image_id, 
                        contents = contents)
                        
            return VDOM_object.wysiwyg(self, contents=result)
        
        width = self.width if self.width else 50
        height = self.height if self.height else 50
        
        if self.image: 
            result = \
                u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <image href="#Res({image})" x="0" y="0" width="{width}" height="{height}"/>
                        </svg>{contents}
                        <svg>
                            <rect x="{rleft}" y="{rtop}" width="{rwid}" height="{rhei}" fill="#FFFFFF" fill-opacity=".0" {bord}/>
                        </svg>
                    </container>
                """.format(
                        id = self.id, vis = self.visible, zind = self.zindex,
                        hierarchy = self.hierarchy, order = self.order,
                        top = self.top, left = self.left, width = width, height = height,
                        image = self.finalimage, contents = contents,
                        rleft = bw/2, rtop = bw/2, rwid = int(self.width)-bw, rhei = int(self.height)-bw, bord = border_string)
        else:
            fontsize = u"""fontsize="%s" """ % self.fontsize if self.fontsize else u""
            label = u"<![CDATA[%s%s]>" % (self.text, "]")
                    
            result = \
                u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                            top="{top}" left="{left}" width="{width}" height="{height}">
                        <svg>
                            <rect x="{rec_left}" y="{rec_top}" width="{rec_wid}" height="{rec_hei}" fill="#FFFFFF" {bord}/>
                        </svg>
                        <text top="{txt_top}" left="{txt_left}" width="{txt_wid}" textalign="{align}" 
                            color="#{color}" fontstyle="{fstyle}" 
                            textdecoration="{txt_decor}" fontweight="{fweight}" fontfamily="{ffamily}" {fsize}>
                            {label}
                        </text>{contents}
                    </container>
                """.format(
                        id = self.id, vis = self.visible, zind = self.zindex, 
                        hierarchy = self.hierarchy, order = self.order, 
                        top = self.top, left = self.left, width = self.width, height = self.height, 
                        rec_left = bw/2, rec_top = bw/2, rec_wid = int(self.width)-bw, rec_hei = int(self.height)-bw,
                        bord = border_string,
                        txt_top = bw, txt_left = bw, txt_wid = int(self.width)-2-2*bw,
                        align = self.align, color = self.color, fstyle = self.fontstyle, 
                        txt_decor = self.textdecoration,
                        fweight = self.fontweight, ffamily = self.fontfamily.replace('"', '').replace("'", ''),
                        fsize = fontsize, label = label, contents = contents)
        return VDOM_object.wysiwyg(self, contents=result)

# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
    # o = application.objects.search(object_id)
    o = object
    # if "image" in param and not "width" in param and not "height" in param:
    if "image" in attributes and not "width" in attributes and not "height" in attributes:
        # res_id = param["image"]["value"]
        res_id = attributes["image"]
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
    
    pro_suite = """#%(id)s {height: 33px !important}
#%(id)s a {
 text-align:center !important;
 background:#fff url("/c016ef5e-c636-586d-9841-f3ff499831aa.png") !important;
 background-repeat:repeat-x;
 background-position:bottom center;
 text-decoration:none;
 line-height:25px;
 border:1px solid #c5c5c5;
 border-radius: 6px;
 -moz-border-radius:6px;
 -webkit-border-radius: 6px;
 -o-border-radius:6px;
 -ms-border-radius: 6px;
 cursor:pointer;
 outline:none !important;
 height:26px !important;
 box-shadow:inset 0px 0px 3px #fff;
    -moz-box-shadow:inset 0px 0px 3px #fff;
    -webkit-box-shadow:inset 0px 0px 3px #fff;
 -o-box-shadow:inset 0px 0px 3px #fff;
 -ms-box-shadow:inset 0px 0px 3px #fff;
 -webkit-transition: all 0.7s ease;
    -moz-transition: all 0.7s ease;
 -o-transition: all 0.7s ease;
}
#%(id)s a:hover {
 box-shadow:inset 0px 0px 6px #fff;
    -moz-box-shadow:inset 0px 0px 6px #fff;
    -webkit-box-shadow:inset 0px 0px 6px #fff;
 -o-box-shadow:inset 0px 0px 6px #fff;
 -ms-box-shadow:inset 0px 0px 6px #fff;
 border:1px solid #a8a8a8;
}
#%(id)s a span {
 line-height:22px !important;
 font-size:14px;
}
#%(id)s a span {
 line-height:22px !important;
 font-size:14px;
color:#000;
font-family:Arial,sans-serif;
}
#%(id)s a.disabled span {
color: #999 !important;
}"""
    # if "skin" in param:
    #     if param["skin"]["value"] == "1":
    #         o.set_attributes({"style": pro_suite})
    if "skin" in attributes:
        if attributes["skin"] == "1":
            o.attributes.update(style=pro_suite)
    # if "style" in param and param["style"]["value"] and o.attributes.style != pro_suite:        
    #     o.set_attributes({"skin": 0})
    if "style" in attributes and attributes["style"] and o.attributes.style != pro_suite:        
        o.attributes.update(skin=0)
    return ""

    
