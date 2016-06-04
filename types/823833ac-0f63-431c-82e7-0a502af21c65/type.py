
import sys


class VDOM_uploader(VDOM_object):

	def render(self, contents=""):
		display = u"display: none;" if self.visible == "0" else u""
		style = u"z-index:{zind}; position:{pos}; top:{top}px; left:{left}px; width:{width}px; {display}"\
			.format(
				zind = self.zindex, pos = self.position, top = self.top, left = self.left,
				width = self.width, height = self.height, display = display)

		woid = (self.id).replace('-', '_')
		id = u"o_" + woid

		classname = u"""class="%s" """ % self.classname if self.classname else u""

		js = u"""<script type='text/javascript'>
			$j(function($){
				$('#%(id)s input').change(function() {
					$('#%(id)s input').each(function() {
						var name = this.value;
						//var fileTitle = name.replace(/.*\\(.*)/g, "$1");
						//fileTitle = fileTitle.replace(/.*\/(.*)/g, "$1");
						execEventBinded('%(woid)s', "change", {title:name});
					});
				});
			});
			</script>
			""" % { "id": id, "woid": woid }

		result = u"""
			<style>{skin}</style>
			<div style="{style}" id="{id}" {classname}>
				<div class="label" style="display:none">{text}</div>
				<input type="file" name="{name}" {control_width} tabindex="{tabind}" />
			</div>
			{js}
			""".format(
					id = id, name = self.name, style = style, tabind = self.tabindex, classname = classname,
					text = self.text, js = js, 
					skin = self.style % { "id": id },
					control_width = u'size="2"' if int(self.skin) == 1 else u'size="%s"' % ((int(self.width) - 96) / 7 + 1)
					)

		return VDOM_object.render(self, contents=result)


	def wysiwyg(self, contents=""):

		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
						top="{top}" left="{left}" width="{width}" height="{height}">
					<svg>
						<rect x="{r1_left}" y="{r1_top}" width="{r1_wid}" height="{r1_hei}" fill="#FFFFFF" stroke="#000000"/>
						<rect x="{r2_left}" y="{r2_top}" width="{r2_wid}" height="{r2_hei}" fill="#CCCCCC" stroke="#000000"/>
					</svg>
					<text top="{txt_top}" left="{txt_left}" width="{txt_wid}" color="#000000" textalign="center">{value}</text>
					{contents}
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex,
					hierarchy = self.hierarchy, order = self.order,
					top = self.top, left = self.left, width = self.width, height = self.height,
					r1_left = 0, r1_top = 0, r1_wid = int(self.width) - 87, r1_hei = int(self.height) - 1,
					r2_left = int(self.width) - 80 , r2_top = 0, r2_wid = 79, r2_hei = int(self.height) - 1,
					txt_top = int(self.height)/2 - 9, txt_left = int(self.width) - 80, txt_wid = 79,
					value = "Browse...", contents = contents)

		return VDOM_object.wysiwyg(self, contents=result)


def set_attr(app_id, object_id, param):
	o = application.objects.search(object_id)

	pro_suite = """
#%(id)s {
	height: 33px;
	overflow: hidden;
}
#%(id)s .label {
	display: block !important;
	text-align: center;
	background: #fff url("/c016ef5e-c636-586d-9841-f3ff499831aa.png") bottom center repeat-x !important;
	text-decoration: none;
	line-height: 25px;
	border: 1px solid #c5c5c5;
	-webkit-border-radius: 6px;
	-moz-border-radius:6px;
	-ms-border-radius: 6px;
	-o-border-radius:6px;
	border-radius: 6px;
	cursor: pointer;
	outline: none !important;
	height: 26px !important;
	-webkit-box-shadow:inset 0 0 3px #fff;
	-moz-box-shadow:inset 0 0 3px #fff;
	-ms-box-shadow:inset 0 0 3px #fff;
	-o-box-shadow:inset 0 0 3px #fff;
	box-shadow:inset 0 0 3px #fff;
	-webkit-transition: all 0.7s ease;
	-moz-transition: all 0.7s ease;
	-ms-transition: all 0.7s ease;
	-o-transition: all 0.7s ease;
	transition: all 0.7s ease;
	line-height: 24px !important;
	font-size: 14px;
	color: #000;
	font-family: Arial,sans-serif;
}
#%(id)s .label:hover {
	-webkit-box-shadow:inset 0 0 6px #fff;
	-moz-box-shadow:inset 0 0 6px #fff;
	-ms-box-shadow:inset 0 0 6px #fff;
	-o-box-shadow:inset 0 0 6px #fff;
	box-shadow:inset 0 0 6px #fff;
	border: 1px solid #a8a8a8;
}
#%(id)s input {
	margin-top: -50px;
	margin-left:-410px;
	-moz-opacity: 0;
	filter: alpha(opacity=0);
	opacity: 0;
	font-size: 150px;
	height: 100px;
}
"""
	if "skin" in param:
		if param["skin"]["value"] == "1":
			o.set_attributes({"style": pro_suite})
	if "style" in param and param["style"]["value"] and o.attributes.style != pro_suite:
		o.set_attributes({"skin": 0})
	return ""


