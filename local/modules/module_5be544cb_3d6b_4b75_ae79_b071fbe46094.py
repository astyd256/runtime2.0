# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



class VDOM_formbutton(VDOM_object):

	def render(self, contents=""):
		display = u"display:none;" if self.visible == "0" else u""
		type = ["submit", "reset", "button"][int(self.attributes["type"])]
		if self.classname == "":
			 clname = ""
		else:
			 clname = "class='%s'" % (self.classname).replace("'", "")
		style = \
			u"{disp} z-index:{zind}; position:{pos}; top:{top}px; left:{left}px; width:{wid}px; height:{hei}px; font:12px tahoma" \
			.format(disp = display, zind = self.zindex, pos = self.position, 
					top = self.top, left = self.left, wid = self.width, hei = self.height)
		id = u"o_" + (self.id).replace('-', '_')

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='formbutton' objname='%s'" % ( (self.label).replace("'", "") )
		else:
			debug_info = u""

		result = u"""<style type="text/css">{css}</style>
<input {debug_info} id="{id}" name="{name}" style="{style}" type="{type}" tabindex="{tabind}" value="{label}" {clname} />
			""".format(
					debug_info = debug_info,
					css = self.style % {"id": id},
					id = id,
					name = self.name,
					style = style,
					type = type,
					tabind = self.tabindex,
					label = self.label,
					clname = clname)
			
		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		label = u"<![CDATA[%s%s]>" % (self.label, "]")
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
					top="{top}" left="{left}" width="{width}" height="{height}">
					<svg>
						<rect x="0" y="0" width="{rec_wid}" height="{rec_hei}" fill="#CCCCCC" stroke="#000000"/>
					</svg>
					<text top="{txt_top}" width="{txt_wid}" color="#000000" textalign="center">{label}</text>{contents}
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex, 
					hierarchy = self.hierarchy, order = self.order, 
					top = self.top, left = self.left, width = self.width, height = self.height,
					rec_wid = int(self.width)-1, rec_hei = int(self.height)-1,
					txt_top = int(self.height)/2-9, txt_wid = int(self.width)-4, label = label,
					contents = contents)
				
		return VDOM_object.wysiwyg(self, contents=result)
		
def set_attr(app_id, object_id, param):
	
	pro_suite = """#%(id)s {
text-align:center !important;
background:#fff url("/f704b515-d69d-24d9-5e81-8dc0984592fa.png") !important;
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
line-height:22px !important;
font-size:14px !important;
color:#000;
font-family:Arial,sans-serif;
}
#%(id)s:hover {
box-shadow:inset 0px 0px 6px #fff;
-moz-box-shadow:inset 0px 0px 6px #fff;
-webkit-box-shadow:inset 0px 0px 6px #fff;
-o-box-shadow:inset 0px 0px 6px #fff;
-ms-box-shadow:inset 0px 0px 6px #fff;
border:1px solid #a8a8a8;
}"""
		
	o = application.objects.search(object_id)
		
	# set attributes
	
	if "skin" in param:
		if param["skin"]["value"] == "1":
			o.set_attributes({"style": pro_suite})
	if "style" in param and param["style"]["value"] and o.attributes.style != pro_suite:		
		o.set_attributes({"skin": 0}) 	
	
	return ""	

		
