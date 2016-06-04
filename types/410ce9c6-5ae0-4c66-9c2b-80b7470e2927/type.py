
class VDOM_formtext(VDOM_object):

	def render(self, contents=""):
		display = u"display: none;" if self.visible == "0" else u""

		if self.mode == "1":
			mode = u"""readonly="readonly" """
		elif self.mode == "2":
			mode = u"""disabled="disabled" """
		else:
			mode = u""
				
		auto = u"off" if self.autocomplete == "0" else u"on"

		clean_id = (self.id).replace('-', '_')
		id = u"o_%s" % clean_id

		# for doctype xhtml 1.0 - width|height depends on padding
		fixw = int(self.width) - 10
		fixh = int(self.height) - 4

		border = u"border-width: 0px;" if self.multiline == "0" and self.border == "0" else u""
		
		style = u"""z-index: {zind}; position: {pos}; top: {top}px; left: {left}px; width: {width}px; height: {height}px;
					padding: 2px 5px; {display} {border} font: 14px tahoma
				""".format(zind = self.zindex, pos = self.position, top = self.top, left = self.left, 
						width = fixw, height = fixh, display = display, border = border)

		if self.title == "":
			title = u""
		else:
			title = u"title=\"%s\"" % (self.title).replace('"', '&quot;')

		if self.placeholder == "":
			placeholder = u""
		else:
			placeholder = u"placeholder=\"%s\"" % (self.placeholder).replace('"', '&quot;')

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='formtext' objname='%s' ver='2012-02-6'" % self.name
		else:
			debug_info = u""

		if self.multiline == "0":
			result = u"""<input {debug_info} id="{id}" name="{name}" style="{style}" type="text" tabindex="{tabind}" 
							value="{value}" class="{classn}" autocomplete="{auto}" {mode} {title} {placeholder} />
					""".format(id = id, name = self.name, style = style, tabind = self.tabindex, debug_info = debug_info,
							value = unicode(self.value).replace('"', '&quot;'), classn = self.classname, auto = auto,
							mode = mode, placeholder = placeholder, title = title)
		else:
			result = u"""<textarea {debug_info} id="{id}" name="{name}" tabindex="{tabind}" 
							style="{style}" class="{classn}" {mode} {title} {placeholder}>{value}</textarea>
					""".format(id = id, name = self.name, tabind = self.tabindex, debug_info = debug_info,
							style = style, classn = self.classname, mode = mode, value = self.value, placeholder = placeholder, title = title)

		focused = u"$q('#%s').focus();" % id if self.focused == "1" else ""

		result += u"""<script type='text/javascript'>
$j(document).ready(function(){
	$j('#%(id)s').blur(function(){
		var x = $j.trim($j(this).val());
		execEventBinded("%(clean_id)s", "blur", { itemValue: x, charCount: x.length });
	});
	$j('#%(id)s').focusin(function(){
		execEventBinded("%(clean_id)s", "focus", {});
	});
	%(focused)s
});</script>""" % { "id": id, "clean_id": clean_id, "focused": focused }

		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		
		disabled = u""" disabled="disabled" """ if self.mode=="2" else u""
		border = u"border-width:0;" if self.multiline == "0" and self.border == "0" else u""
		placeholder = u"placeholder=\"%s\"" % (self.placeholder).replace('"', '&quot;') if self.placeholder!="" else u""
		
		style = u""" style="width: {width}px; height: {height}px; background-color:#ffffff; font: 14px tahoma; padding: 2px 5px; {border}" """.format(
			border = border,
			width = self.width, height = self.height)
		
		if self.multiline == "1" : #multiline
			text = \
				u"""<textarea objtype="formtext" {style} {disabled} {placeholder}>
						{value}
					</textarea>
				""".format(
						width = self.width, height = self.height,
						value = self.value, placeholder = placeholder,
						disabled = disabled, 
						style = style)
		else : #singleline
			text = u"""<input objtype="formtext" value="{value}" {style} {disabled} {placeholder}/>""".format(
				width = self.width, height = self.height,
				value = self.value, placeholder = placeholder,
				disabled = disabled,
				style = style)
			
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
						top="{top}" left="{left}" width="{width}" height="{height}" >
					<htmltext top="0" left="0" width="{width}" height="{height}" overflow="hidden" blendMode="normal">
						{text}
					</htmltext>
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex, 
					hierarchy = self.hierarchy, order = self.order, 
					top = self.top, left = self.left, 
					width = self.width, height = self.height,
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


