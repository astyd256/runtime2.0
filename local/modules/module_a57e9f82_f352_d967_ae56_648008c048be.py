# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



class VDOM_formcolorpicker(VDOM_object):

	def render(self, contents=""):
		self.set_color_value()

		display = u"display: none;" if self.visible == "0" else u""

		if self.mode == "1":
			mode = u"""readonly="readonly" """
		elif self.mode == "2":
			mode = u"""disabled="disabled" """
		else:
			mode = u""

		clean_id = (self.id).replace('-', '_')
		id = u"o_%s" % clean_id

		# for doctype xhtml 1.0 - width|height depends on padding
		fixw = int(self.width) - 10
		fixh = int(self.height) - 4

		border = u"border-width: 0px;" if self.border == "0" else u""
		hide = u"true" if self.mode == "1" else u"false"
		title_OK = (self.titleok).replace('"', "'")
		title_Canc = (self.titlecancel).replace('"', "'")

		div_style = u"z-index: {zind}; position: absolute; top: {top}px; left: {left}px; {display}" \
			.format(zind = self.zindex, top = self.top, left = self.left, display = display)

		inp_style = u"""position: relative; width: {width}px; height: {height}px; padding: 2px 5px;
			margin-right: 2px; font: 14px tahoma; {border} """ \
			.format(width = fixw, height = fixh, border = border)

		result = \
			u"""<div id="%(id)s" style="%(div_style)s"><input id="inp_%(id)s" class='formcolorpicker' name="%(name)s" style="%(inp_style)s" type="text" tabindex="%(tabind)s" value="%(value)s" /></div>
<script type="text/javascript">$j(document).ready(function(){
	$j("#inp_%(id)s").colorInput({
		hideInput:%(hide)s,textAccept:"%(title_OK)s",textCancel:"%(title_Canc)s",
		change:function(){
			execEventBinded("%(clean_id)s","changecolor",{color:this.value});
		}
	});
});</script>""" % {"div_style": div_style, "id": id, "name": self.name,
					"inp_style": inp_style, "tabind": self.tabindex, "value": self.value,
					"hide": hide, "title_OK": title_OK, "title_Canc": title_Canc, "clean_id": clean_id}

		return VDOM_object.render(self, contents=result)

	def get_btn_properties (self):
		form_width = int(self.width)
		try:
			object = application.objects.search(self.id)
			if object and object.parent:
				form_obj=application.objects.search(object.parent.id)
				if form_obj:
					form_width=int(form_obj.attributes.width)
		except Exception:
			form_width = int(self.width)

		distance = 2

		btn_width = btn_height = 20

		if self.mode == "1": # "hide"
			btn_x = btn_y = 0
		else:
			btn_x = int(self.width) + distance
			btn_y = (int(self.height)-btn_height)/2

			obj_max_right = int(self.left)+int(self.width)+distance+btn_width
			if form_width < obj_max_right:
				btn_x = 0
				btn_y = int(self.height)

		return btn_x, btn_y, btn_width, btn_height

	def set_color_value (self) :
		if self.value :
			if not self.value.startswith("#") :
				self.value = u"#" + self.value
		else:
			self.value = "#cccccc"

	def wysiwyg(self, contents=""):
		self.set_color_value()

		text_size = self.width if self.value else 0

		btn_x, btn_y, btn_width, btn_height = self.get_btn_properties()

		text_y = 0 if self.height <= 22 else (int(self.height)-20)/2
		text = "" if self.mode == "1" else u"""<text x="3" y="{text_y}" width="{txt_wid}" height="20" align="left" color="#000000" font-family="tahoma" font-size="14">{value}</text>""" \
			.format(
				txt_wid = text_size,
				value = self.value,
				text_y = text_y)

		input_stroke = "" if self.border == "0" else u""" stroke="#aaaaaa" """
		rect_input = "" if self.mode == "1" else u"""<rect x="0" y="0" width="{rec_wid}" height="{rec_hei}" fill="#FFFFFF" {stroke}/>""".format(
			rec_wid = int(self.width) - 1,
			rec_hei = int(self.height) - 1,
			stroke = input_stroke)

		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
						top="{top}" left="{left}" width="{width}" height="{height}" >
					<svg>
						{rect_input}
						<rect x="{btn_x}" y="{btn_y}" width="{btn_width}" height="{btn_height}" fill="{color}"/>
						{text}
					</svg>
			 	</container>
			 """.format(
					id = self.id, vis = self.visible, zind = self.zindex,
					hierarchy = self.hierarchy, order = self.order,
					top = self.top, left = self.left,
					width = self.width, height = self.height,
					color = self.value,
					btn_x = btn_x, btn_y = btn_y,
					btn_width = btn_width,
					btn_height = btn_height,
					rect_input = rect_input,
					text = text)

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



