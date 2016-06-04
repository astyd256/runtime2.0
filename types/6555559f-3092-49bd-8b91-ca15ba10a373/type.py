
class VDOM_formpassword(VDOM_object):

	def render(self, contents=""):

		display = u"display:none;" if self.visible == "0" else u""
		fixw = int(self.width) - 10
		fixh = int(self.height) - 4
		bord = u"border-width: 0px;" if self.border == "0" else u""

		style = u"""position: {pos}; z-index: {zind}; top: {top}px; left: {left}px; width: {width}px; height: {height}px;
					padding: 2px 5px 2px 5px; {display} font: 14px tahoma; {border}
				""".format(pos = self.position, zind = self.zindex, top = self.top, left = self.left, 
						width = fixw, height = fixh, display = display, border = bord)

		auto = u"off" if self.autocomplete == "0" else u"on"
		id = u"o_" + (self.id).replace('-', '_')
		
		result = u"""<input id="{id}" name="{name}" style="{style}" type="password" 
						tabindex="{tabind}" value="{value}" class="{cname}" autocomplete="{auto}" />
				""".format(id = id, name = self.name, style = style, tabind = self.tabindex, 
						value = self.value, cname = self.classname, auto = auto)

		return VDOM_object.render(self, contents=result)


	def wysiwyg(self, contents=""):

		rect_width = int(self.width)-1
		rect_height = int(self.height)-1
		
		value = u"*" * len(self.value) if self.value else u""
		stroke = u""" stroke="#888888" """ if self.border=="1" else u""
		
		result = u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
							top="{top}" left="{left}" width="{width}" height="{height}">
						<svg>
							<rect x="0" y="0" width="{rect_width}" height="{rect_height}" fill="#FFFFFF" {stroke}/>
						</svg>
						<svg>
							<text x="{text_x}" y="{text_y}" width="{text_width}" height="{height}">{value}</text>
						</svg>
					</container>
				""".format(id = self.id, vis = self.visible, zind = self.zindex, 
						hierarchy = self.hierarchy, order = self.order, 
						top = self.top, left = self.left, 
						width = self.width, height = self.height, 
						rect_width = rect_width, rect_height = rect_height,
						text_width = rect_width-7,
						text_x = 7, text_y = 15 if rect_height < 15 else (rect_height-15)/2+15,
						value = value,
						stroke = stroke)
						
		return VDOM_object.wysiwyg(self, contents=result)

def set_attr(app_id, object_id, param):
	o = application.objects.search(object_id)
	
	if "width" in param:
		width = param["width"]["value"]
		if int(width) < 10:
			o.set_attributes({"width": "10"})

	if "height" in param:
		height = param["height"]["value"]
		if int(height) < 4:
			o.set_attributes({"height": "4"})
			
