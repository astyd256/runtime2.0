
class VDOM_codeeditor(VDOM_object):

	def render(self, contents=""):
		id = u"o_" + (self.id).replace('-', '_')

		display = u"display:none;" if self.visible == "0" else u"display:block;"

		style = u"""z-index: {zind}; top: {top}px; left: {left}px; overflow: visible; position: absolute;
			width: {width}px; height: {height}px; padding: 2px 5px 2px 5px; {display} font: 14px tahoma
			""".format(zind = self.zindex, top = self.top, left = self.left,
					width = self.width, height = self.height, display = display)

		style_area = u"""width:{width}px; height:{height}px""".format(width = self.width, height = self.height)

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='codeeditor' objname='%s' ver='%s'" % (self.name, self.type.version)
		else:
			debug_info = u""

		result = u"""
<style type="text/css">
#%(id)s .CodeMirror-scroll { height: %(height)spx; }
</style>
<div id="%(id)s" style="%(style)s" %(debug_info)s>
	<textarea name="%(name)s" style='%(style_area)s'>%(value)s</textarea>
</div>
<script type="text/javascript">$q(function(){
	if (typeof window.%(id)s_codeeditor !== 'undefined') {
		window.%(id)s_codeeditor.toTextArea();
		delete(window.%(id)s_codeeditor);
	}
	window.%(id)s_codeeditor = CodeMirror.fromTextArea($q('#%(id)s>textarea').get(0), {
		mode: '%(mode)s',
		lineNumbers: true,
		styleActiveLine: true,
		onCursorActivity: function() { window.%(id)s_codeeditor.matchHighlight("CodeMirror-matchhighlight"); }
	});
	$q('#%(id)s').parents('form:first').submit(function(){
		window.%(id)s_codeeditor.save();
	});
	window.%(id)s_codeeditor.refresh();
});</script>
			""" % {
				"mode":       self.syntax,
				"id":         id,
				"name":       self.name,
				"style":      style,
				"style_area": style_area,
				"value":      unicode(self.value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;'),
				"width":      self.width,
				"height":     self.height,
				"debug_info": debug_info
			}

		return VDOM_object.render(self, contents=result)

	def get_lines_amount (self, value) : 			
		count = value.count("\n")
		
		return int(count)+1
	
	def get_lines_text (self, value, text_height) :
		
		amount = self.get_lines_amount(value)
		
		lines = \
			u""" <text x="0" y="2" width="28" height="{text_height}" 
					font-family="tahoma" font-size="14" fill="#aaaaaa" align="right"> 
			""".format(text_height=text_height)
		
		i = 1
		while (i <= amount):
			text_y = (i-1)*17
			
			if text_y >= text_height :
				i = i + 1
				break
				
			text_h = 20 if text_y + 20 <= text_height else text_height-text_y
			lines += u""" <tspan y="{y}" height="{height}">{line_number}</tspan> """.format(y=text_y, line_number=i, height=text_h)
			i = i + 1
		
		lines += u" </text> "
		
		return lines
		
	def wysiwyg(self, contents=""):
		
		text_width = int(self.width) - 38
		text_height = int(self.height) - 2

		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
					top="{top}" left="{left}" width="{width}" height="{height}" 
					backgroundcolor="#ffffff" bordercolor="#cccccc">
					<svg>
						<rect x="1" y="1" width="28" height="{text_height}" fill="#F7F7F7"/>
						<line x1="30" y1="1" x2="30" y2="{line_y_end}" style="stroke:#eeeeee"/>
						<text x="40" y="17" width="{text_width}" height="{text_height}" font-family="Courier New" font-size="14">{value}</text>
						{lines}
					</svg>
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex,
					hierarchy = self.hierarchy, order = self.order,
					top = self.top, left = self.left, 
					width = self.width, height = self.height,
					text_width = text_width, text_height = text_height,
					line_y_end = 1+int(self.height)-2,
					value = self.value,
					lines = self.get_lines_text(self.value, text_height))

		return VDOM_object.wysiwyg(self, contents=result)


