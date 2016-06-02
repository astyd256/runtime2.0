# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



class VDOM_Sensitive(VDOM_object):

	def render(self, contents=""):
		display = u"display:none" if self.visible != "1" else ""

		target = ""
		if self.target:
			target = u""" target="{target}" """.format(target = self.target)

		if self.link:
			link_render_1 = u"""<a href="{link}" {target}>""".format(link = self.link, target = target)
			link_render_2 = u"</a>"
		elif self.containerlink:
			ref_obj = application.objects.search(self.containerlink)
			ref_page = u"/{page_name}.vdom".format(page_name = ref_obj.name) if ref_obj else ""
			link_render_1 = u"""<a href="{page}" {target}>""".format(page = ref_page, target = target)
			link_render_2 = u"</a>"
		else:
			link_render_1 = ""
			link_render_2 = ""

		link_image = u"""<img style="width:{width}px; height:{height}px; border:none;" """ \
			u"""src="/7d0e6d03-2fc2-4e3d-9c6b-acab5c2e97d5.res" >""".format(width = self.width, height = self.height)

		bw = 0
		if self.border != "0":
			bw = int(self.border)
			minsize = min(int(self.width), int(self.height))
			if (bw > minsize / 2):
				bw = minsize / 2

		style = \
			u"""position: absolute; z-index: {zindex}; left: {left}px; top: {top}px; width: {width}px; """ \
			u"""height: {height}px; border:{bw}px solid black; overflow: hidden; {display} """.format(
				zindex = self.zindex,
				left = self.left,
				top = self.top,
				width = self.width,
				height = self.height,
				display = display,
				bw = str(bw))

		id = 'o_' + (self.id).replace('-', '_')

		result = u"""<div id="{id}" style="{style}">{link}</div>""".format(
			id = id,
			style = style,
			link = link_render_1 + link_image + link_render_2)

		return result

	def wysiwyg(self, contents=""):

		bw = 0
		s = ""
		if (self.border != "0") & (self.border != ""):
			bw = int(self.border)
			minsize = min(int(self.width), int(self.height))
			if (bw > minsize / 2):
				bw = minsize / 2
			s = u""" stroke="#000000" stroke-width="{bw}" """.format(bw = bw)


		result=\
			u"""<container id="{id}" visible="{visible}" zindex="{zindex}" hierarchy="{hierarchy}" order="{order}"
						top="{top}" left="{left}" width="{width}" height="{height}">
					<svg>
						<rect x="{x}" y="{y}" width="{rect_width}" height="{rect_height}" fill="#EEEEEE" fill-opacity=".4" {stroke}/>
					</svg>
					{contents}
				</container>
			""".format(
					id = self.id,
					visible = self.visible,
					zindex = self.zindex,
					hierarchy = self.hierarchy,
					order = self.order,
					top = self.top,
					left = self.left,
					width = self.width,
					height = self.height,
					x = bw / 2,
					y = bw / 2,
					rect_width = int(self.width) - bw,
					rect_height = int(self.height) - bw,
					stroke = s,
					contents = contents)

		return VDOM_object.wysiwyg(self, contents=result)

	
