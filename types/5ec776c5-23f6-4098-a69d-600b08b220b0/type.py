
from scripting import e2vdom

class VDOM_formradiogroup(VDOM_object):

	def render(self, contents=""):
		e2vdom.process(self)
		display = u"display:none" if self.visible == "0" else u""
		
		style = u"""overflow: auto; z-index: {zind}; position: {pos};
					top: {top}px; left: {left}px; width: {width}px; height: {height}px; {display}
		""".format( zind = self.zindex, pos = self.position, 
				top = self.top, left = self.left, width = self.width, height = self.height, display = display)
		
		id = u"o_" + (self.id).replace('-', '_')
		result = u"""<div id="{id}" style="{style}">{contents}</div>""".format(id = id, style = style, contents = contents)
		
		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		if len(contents) == 0:
			from scripting.utils.wysiwyg import get_empty_wysiwyg_value
			
			image_id = "1ac76095-3282-e956-f43a-171ce744e574"
			result = get_empty_wysiwyg_value(self, image_id)
			
			return VDOM_object.wysiwyg(self, contents=result)
			
		result = u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
							top="{top}" left="{left}" width="{width}" height="{height}">
						<svg>
							<rect top="0" left="0" width="{rec_wid}" height="{rec_hei}" fill="#EEEEEE" stroke="#000000"/>
						</svg>
						{contents}
					</container>""".format(id = self.id, vis = self.visible, zind = self.zindex, 
									hierarchy = self.hierarchy, order = self.order, 
									top = self.top, left = self.left, 
									width = self.width, height = self.height, 
									rec_wid = int(self.width) - 1, rec_hei = int(self.height) - 1,
									contents = contents)
		return VDOM_object.wysiwyg(self, contents=result)

