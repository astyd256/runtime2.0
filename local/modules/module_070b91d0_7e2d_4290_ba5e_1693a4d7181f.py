# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



class VDOM_formtextarea(VDOM_object):

	def render(self, contents=""):
		display = u"display:none;" if self.visible == "0" else u""
		id = u"o_" + (self.id).replace('-', '_')			

		style = u"""z-index: {zind}; position: {pos}; top: {top}px; left: {left}px;
					width: {width}px; height: {height}px; padding: 2px 5px 2px 5px; {display} font: 14px tahoma
				""".format(zind = self.zindex, pos = self.position, top = self.top, left = self.left, 
						width = self.width, height = self.height, display = display)

		result = u"""<textarea id="{id}" name="{name}" tabindex="{tabind}" style="{style}">{value}</textarea>"""\
				.format(id = id, name = self.name, tabind = self.tabindex, style = style, value = self.value)

		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
						top="{top}" left="{left}" width="{width}" height="{height}" >
					<htmltext top="0" left="0" width="{width}" height="{height}" overflow="hidden" blendMode="normal">
						<textarea style="width: {width}px; height: {height}px; background-color:#ffffff; font: 14px tahoma; padding: 2px 5px;">
							{value}
						</textarea>
					</htmltext>
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex, 
					hierarchy = self.hierarchy, order = self.order, 
					top = self.top, left = self.left, 
					width = self.width, height = self.height,
					value = self.value)
		
		return VDOM_object.wysiwyg(self, contents=result)
		
