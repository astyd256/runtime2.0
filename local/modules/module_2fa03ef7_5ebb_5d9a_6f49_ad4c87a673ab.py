# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



import collections, json, StringIO



def on_update(object, attributes):
	css = """"""
	# if "skin" in param:
	# 	if param["skin"]["value"] == "1":
	# 		o.set_attributes({"style": css})
	if attributes.get("skin") == "1":
		object.attributes.update(style=css)
	# if "style" in param and param["style"]["value"] and o.attributes.style != css:
	# 	o.set_attributes({"skin": 0})
	if attributes.get("style") and object.attributes["style"] != css:
		object.attributes.update(skin=0)


class VDOM_list(VDOM_object):

	def render(self, contents=""):

		woid = (self.id).replace('-', '_')
		id = u"o_" + woid

		display = u" display:none; " if self.visible == "0" else u""

		style = u"""{display}z-index: {zind}; position: absolute; top: {top}px; left: {left}px; height: {height}px; width: {width}px"""\
				.format(display = display, zind = self.zindex, top = self.top, left = self.left, height = self.height, width = self.width)

		if self.cssclass != "" or self.selectionmode == "1":
			cssclass = u"class='%s %s'" % ( self.cssclass if self.cssclass else "", u"multiselect" if self.selectionmode == "1" else "" )
		else:
			cssclass = ""

		if self.data:
			try:
				data = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
				if isinstance(data, int):
					raise Exception (u"Incorrect value in data %s" % self.data)
			except:
				raise Exception (u"Incorrect value in data %s" % self.data)
		else:
			data = {}

		selectedRows = []
		if self.selectedrows:
			try:
				selectedRows = json.loads(self.selectedrows)
				if isinstance(selectedRows, list):
					js_multiselect = ""
				else:
					raise Exception (u"Attribute must be list")
			except:
				raise Exception (u"Incorrect value in selected rows")
		else:
			js_multiselect = u""


		hlayout = u"#%(id)s ul li{display: inline;}" % {"id": id} if self.layout == "1" else u""

		css = u"#%(id)s ul{list-style: none outside none;margin: 0;padding: 0;}%(hlayout)s" % {"id": id, "hlayout": hlayout}

		res_buffer = StringIO.StringIO(u"")
		res_buffer.write(u"<style type='text/css'>")
		res_buffer.write(css)
		css = self.style % {"id": id}
		res_buffer.write(css)
		res_buffer.write(u"</style>")

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='list' objname='%s' ver='%s'" % (self.name, self.type.version)
		else:
			debug_info = u""

		rslt = u"""<div {debug_info} id="{id}" style="{style}" {cssclass}><ul>""".format(
				debug_info = debug_info,
				name = self.name,
				id = id,
				style = style,
				cssclass = cssclass )
		
		res_buffer.write(rslt)

		for key, value in data.items():
			active = u'class="list-item-%s %s %s"' % ( key, "active" if key == self.selecteditem else "", "selected" if key in selectedRows else "")
			if isinstance(value, list):
				if len(value) == 3:
					image = u"<img src=\"%s\" />" % value[1]
					li = u"<li itemid=\"%(elem_id)s\" %(active)s>%(left_image)s%(content)s%(right_image)s</li>" % {
						"elem_id":     unicode(key),
						"content":     unicode(value[0]),
						"active":      active,
						"left_image":  image if value[2] == "left" else u"",
						"right_image": image if value[2] == "right" else u"" }
					res_buffer.write(li)
				else:
					raise Exception("Must be 3 parameters in string %s" % unicode(value))
			elif isinstance(value, unicode):
				li = u"<li itemid=\"%(elem_id)s\" %(active)s>%(content)s</li>" % {"elem_id": unicode(key), "active": active, "content": unicode(value)}
				res_buffer.write(li)

			else:
				raise Exception("Incorrect value in string %s" % unicode(value))

		if self.dragdrop == "1":
			dragdrop = u"""
$j('#%(id)s li').droppable({
	//greedy: true,
	//activeClass: "ui-state-hover",
	hoverClass: "ui-state-active",
	drop: function(e, ui) {
		execEventBinded('%(woid)s', "drop", {itemid: $j(this).attr('itemid')});
	}
});
			""" % { "id": id, "woid": woid }
		else:
			dragdrop = u""

		if ((self.clickclass).strip() == ""):
			clickclass = u""
		else:
			clickclass = self.clickclass
			clickclass = u".%s" % clickclass.replace(' ', ' .')

		handleclick = u"""
	var %(id)s_doo = false, m = $j('#%(id)s').hasClass('multiselect');
	$j('#%(id)s ul li %(clickclass)s').bind('click dblclick', function(e){
		var tt = $j(this);
		if (tt.is('li')) {
			t = tt;
		} else {
			t = tt.closest('li');
		}
		t.parent().children().removeClass("active");
		if (m) {
			if (t.hasClass("selected")) t.removeClass("selected");
			else t.addClass("selected");
		}
		t.addClass("active");
		if (e.type == 'dblclick') {
			%(id)s_doo = false;
			if (m) {
				var a = [];
				t.parent().find('li.selected[itemid]').each(function(i,e){ a.push($q(e).attr('itemid')); });
				execEventBinded('%(woid)s', "rowsselected", {keyList: a });
			} else {
				execEventBinded('%(woid)s', "itemdblclick", {itemid: t.attr('itemid')});
			}
		} else {
			setTimeout(function() {
				if (%(id)s_doo == true) {
					%(id)s_doo = false;
					if (m) {
						var a = [];
						t.parent().find('li.selected[itemid]').each(function(i,e){ a.push($q(e).attr('itemid')); });
						execEventBinded('%(woid)s', "rowsselected", {keyList: a });
					} else {
						execEventBinded('%(woid)s', "itemclick", {itemid: t.attr('itemid')});
					}
				}
			}, 300);
			%(id)s_doo = true;
		}
		return false;
	});
		""" % { "id": id, "woid": woid, "clickclass": clickclass }

		res_buffer.write(u"</ul></div>")
		js_script = u"""<script type="text/javascript">
$j(function(){
	%(handleclick)s
	%(dragdrop)s
});
</script>""" % { "woid": woid, "id": id, "dragdrop": dragdrop, "handleclick": handleclick }

		res_buffer.write(js_script)
		result = res_buffer.getvalue()
		res_buffer.close()

		return VDOM_object.render(self, contents=result)

		
	def __get_error_wysiwyg_obj (self, error_text) :
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" 
							top="{top}" left="{left}" width="{width}" height="{height}">
					<text top="0" left="5" color="#ff0000" textalign="left">{value}</text>
				</container>
			""".format(
					id = self.id, vis = self.visible, 
					zind = self.zindex, hierarchy = self.hierarchy, 
					top = self.top, left = self.left,
					width = self.width, height = self.height,
					value = error_text)
				
		return VDOM_object.wysiwyg(self, contents=result)
			
			
	def wysiwyg(self, contents=""):
		incorrect_data_text = u"Incorrect value in data:\n{data}".format(data = self.data)

		if self.data:
			try:
				data = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
				if isinstance(data, int):
					return self.__get_error_wysiwyg_obj(incorrect_data_text)
			except:
				return self.__get_error_wysiwyg_obj(incorrect_data_text)
		else:
			data = {}

		if not data :
			import utils.wysiwyg

			image_id = "4a582b3d-09ee-8ac1-1451-08a964bbb510"
			result = utils.wysiwyg.get_empty_wysiwyg_value(self, image_id)
			return VDOM_object.wysiwyg(self, contents=result)

		try:
			items = data.items()

		except:
			return self.__get_error_wysiwyg_obj(incorrect_data_text)

		res_buffer = StringIO.StringIO(u"")
		if self.layout == "1":
			res_buffer.write(u"""<row backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0">""")
			for key, value in items:
				if isinstance(value, list):
					li = u"<cell backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><text fontsize=\"14\" color=\"#000000\" textalign=\"left\">%s</text></cell>" % unicode(value[0])
					res_buffer.write(li)
				elif isinstance(value, unicode):
					li = u"<cell backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><text fontsize=\"14\" color=\"#000000\" textalign=\"left\">%s</text></cell>" % unicode(value)
					res_buffer.write(li)
			res_buffer.write(u"</row>")
		else:
			for key, value in items:
				if isinstance(value, list):
					li = u"<row backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><cell backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><text fontsize=\"14\" color=\"#000000\" textalign=\"left\">%s</text></cell></row>" % unicode(value[0])
					res_buffer.write(li)
				elif isinstance(value, unicode):
					li = u"<row backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><cell backgroundcolor=\"#f0f0f0\" bordercolor=\"#000000\" borderwidth=\"0\"><text fontsize=\"14\" color=\"#000000\" textalign=\"left\">%s</text></cell></row>" % unicode(value)
					res_buffer.write(li)

		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}"
					top="{top}" left="{left}" width="{width}" height="{height}">
					<table zindex="{zind}" top="0" left="0" width="{width}" height="{height}" backgroundcolor="#f0f0f0" bordercolor="#000000" borderwidth="0" >
						{res_buffer}
					</table>
				</container>
			""".format(
				id = self.id, vis = self.visible, zind = self.zindex,
				hierarchy = self.hierarchy,
				top = self.top, left = self.left, 
				width = self.width, height = self.height,
				res_buffer = res_buffer.getvalue())

		res_buffer.close()
		return VDOM_object.wysiwyg(self, contents=result)
