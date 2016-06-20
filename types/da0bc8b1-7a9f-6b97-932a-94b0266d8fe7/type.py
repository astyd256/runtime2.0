
from scripting import e2vdom


class VDOM_accordeon(VDOM_object):

	def render(self, contents=""):

		e2vdom.process(self)

		display = u" display:none; " if self.visible == "0" else u""

		if self.heightauto == "0":
			height = "height:"+self.height+"px;"
		else:
			height = "overflow: visible;"

		style = display + "z-index: %s;position: %s;top: %spx;left: %spx;width: %spx;%s"%(self.zindex, self.position, self.top, self.left, self.width, height)
		clear_id = (self.id).replace('-', '_')
		id = 'o_' + clear_id

		classname = u"""class="%s" """ % self.classname if self.classname else u""

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
		else:
			debug_info = u""

		result = u"""<div %(debug_info)s %(classname)s id="%(id)s" style="%(style)s">%(contents)s</div>
<script type="text/javascript">
$q(function(){
	vdom_accordeon('#%(id)s','%(opened)s');
});
</script>""" % {
			"debug_info": debug_info,
			"id": id, "style": style, "contents": contents,
			"classname": classname, "opened": self.opened}

		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		if len(contents) == 0:
			from scripting.utils.wysiwyg import get_empty_wysiwyg_value
			
			image_id = "f3cba395-7df9-a844-075e-13e34400048d"
			result = get_empty_wysiwyg_value(self, image_id)
			
		else:	
			
			result = \
				u"""<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" 
						order="{order}" top="{top}" left="{left}" width="{width}" height="{height}">
						<svg>
							<rect x="0" y="0" width="{width}" height="{height}" fill="#EEEEEE"/>
						</svg>
						{contents}
						</container>
				""".format(
						id = self.id, visible = self.visible, 
						zindex = self.zindex, hierarchy = self.hierarchy, 
						order = self.order, 
						top = self.top, left = self.left, 
						width = self.width, height = self.height,
						contents = contents)

		return VDOM_object.wysiwyg(self, contents=result)

		
