
class VDOM_formradiobutton(VDOM_object):

	def render(self, contents=""):
		display = u"display:none;" if self.visible == "0" else u""
		classn = u"""class="%s" """ % self.classname if self.classname else u""
		disable = u"disabled='disabled'" if self.disable == "1" else u""
		
		object = application.objects.search(self.id)
		if object.parent and object.parent.type.class_name == "VDOM_formradiogroup":
			name = object.parent.name
			state = [u"", u"""checked="checked" """][int(self.attributes["state"])]
			style = u"""z-index: {zind}; position: absolute; top: {top}px; left: {left}px;
						width: {width}px; height: {height}px; font: 14px tahoma; overflow: hidden; {display}"""\
					.format(zind = self.zindex, top = self.top, left = self.left, 
							width = self.width, height = self.height, display = display)

			clean_id = (self.id).replace('-', '_')
			id = u"o_%s" % clean_id
			
			label_pos = ["position: absolute; left: 20px",
						 "position: absolute; left: 0px"][int(self.align)]
			button_pos = ["position: absolute; left: 0px",
						  "position: absolute; left: {left}px".format(left =  int(self.width) - 20)][int(self.align)]			   
			
			
			result = \
				u"""<div id="%(id)s" style="%(style)s">
						<input %(classn)s name="%(name)s" type="radio" %(state)s tabindex="%(tabind)s" 
							value="%(value)s" id="inp_%(id)s" style="%(inp_style)s" %(disable)s/>
						<label for="inp_%(id)s" style="%(lbl_style)s" title="%(label)s">%(label)s</label>
						%(contents)s
					</div>
					<script type="text/javascript">
						jQuery(document).ready(function(){
							jQuery("#inp_%(id)s").change(function(){
								execEventBinded("%(clean_id)s", "change", { Value: jQuery("#inp_%(id)s").val() });});
						});
					</script>
				""" % { "id": id, "style": style, "classn": classn,
						"name": name, "state": state, "tabind": self.tabindex, "value": self.value,
						"inp_style": button_pos, "disable": disable, "lbl_style": label_pos, 
						"label": self.label, "contents": contents, "clean_id": clean_id}
		else:
			result = u""

		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		
		label_left = 16 if self.align == "0" else 1
		label_width = int(self.width)-label_left
		
		label = \
			u"""<text top="-1" left="{left}" width="{label_width}" height="{label_height}">{label}</text>
			""".format(
					left = label_left,
					label_width = label_width, 
					label_height = self.height,
					label = self.label)
		
		circle_x = 10 if self.align == "0" else int(self.width) - 10
		circle_color = u"#888888" if self.disable=="1" else "#000000"
		
		state_circle = u""
		if int(self.state): # checked
			state_circle = \
				u"""<circle cx="{circle_x}" cy="8.5" r="2" fill="{circle_color}" stroke="{circle_color}"/>
				""".format(
					circle_x = circle_x,
					circle_color = circle_color)
		
		circle = \
			u"""<svg>
					<circle cx="{circle_x}" cy="8.5" r="4.5" fill="#EEEEEE" stroke="{circle_color}"/>
					{state_circle}
				</svg>
			""".format(
					circle_x = circle_x, 
					circle_color = circle_color,
					state_circle = state_circle)
					
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
							top="{top}" left="{left}" width="{width}" height="{height}">
					{circle}
					{label}
					{contents}
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex, 
					hierarchy = self.hierarchy, order = self.order, 
					top = self.top, left = self.left, 
					width = self.width, height = self.height,
					label = label, 
					circle = circle, 
					contents = contents)
									
		
		return VDOM_object.wysiwyg(self, contents=result)

		
