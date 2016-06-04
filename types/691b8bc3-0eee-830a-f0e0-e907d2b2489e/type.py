
from scripting import e2vdom


class VDOM_tabview(VDOM_object):
	
	def render(self, contents=""):
		from collections import OrderedDict
		display = u" display:none; " if self.visible == "0" else u""

		e2vdom.process(self)

		style = u"""{display} z-index: {zind}; position: {pos}; top: {top}px; left: {left}px; width: {width}px; height: {height}px; border: none;""".format(display = display, zind = self.zindex, pos = self.position, 
						top = self.top, left = self.left, width = self.width, height = self.height)

		id = u"o_" + (self.id).replace('-', '_')		
		cont_tag = u"""<div class="content_%s">%s</div>""" % (id, contents)
		tab_tag = u""
		tag_array = {}
		js = u""
		children_array = []
		children = self.objects
		for key in children:
			child = children[key]
			children_array.append([str(child.id), str(child.name), str(child.hierarchy), "o_" + (child.id).replace('-', '_')])
			tag_array[child.hierarchy] = u"""<li><a href='#{id}'>{tabname}</a></li>\n""".format(id = "o_" + (child.id).replace('-', '_'), tabname = child.title) 
			
			if self.currenttab == child.hierarchy:
				show_guid = u"o_" + (child.id).replace('-', '_')
				js = u"""<script type="text/javascript">
$j('#%(id)s div.content_%(id)s').children('div').hide();
$j('#%(id)s #%(show_guid)s').show();
$j('#%(id)s ul.tabNavigation a').removeClass('active');
$j('#%(id)s ul.tabNavigation a[href="#%(show_guid)s"]').addClass('active');
</script>""" % { "id": id, "show_guid": show_guid }
		
		sortTagArray = OrderedDict(sorted(tag_array.items(), key=lambda t: t[0]))
		for key in sortTagArray:
			tab_tag += tag_array[key]
		
		css = u"""
#ul_%(id)s {
	list-style: none outside none;
	margin: 0;
	padding: 0;
}

#ul_%(id)s li {
	display: inline;
}
""" % {"id": id}

		if self.showtabs == '1':
			css += self.style % {"id": id}
			tabs = u'<ul id="ul_%(id)s" class="tabNavigation" style="list-style: none"> %(tab)s </ul>' % {"id": id, "tab": tab_tag}
			js += u"""<script type="text/javascript">
var tabview_children_%(id)s = %(arr)s;
$j(document).ready(function($){
	$("#ul_%(id)s a").click(function(){
		$("#%(id)s>div.content_%(id)s>div").fadeOut(100);
		$("#%(id)s>div.content_%(id)s>div").filter(this.hash).fadeIn(100);
		$('#ul_%(id)s a').removeClass('active');
		$(this).addClass('active');
		var cont_id = this.hash.substring(3, this.hash.length).replace(/_/g, "-")
		for (var i = 0; i<tabview_children_%(id)s.length; i++){
			if (cont_id == tabview_children_%(id)s[i][0]){
				execEventBinded("%(id)s".substring(2, "%(id)s".length), "tabchanged", {ID:tabview_children_%(id)s[i][0], Name:tabview_children_%(id)s[i][1], Hierarchy:tabview_children_%(id)s[i][2]});
			}
		}
		return false;
	});
});
</script>""" % { "id": id, "arr": str(children_array) }
		else:
			css = u''
			tabs = u''
			js += u"""<script type="text/javascript">
var tabview_children_%(id)s = %(arr)s;
</script>""" % { "id": id, "arr": str(children_array) }

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='%s' objname='%s' ver='%s'" % (self.type.name, self.name, self.type.version)
		else:
			debug_info = u""

		result = \
			u"""
<style type="text/css">{css}</style>
<div {debug_info} id="{id}" style="{style}">
	{tabs}
	{cont_tag}
</div>
{js}
			""".format(
					debug_info = debug_info,
					css = css, id = id, style = style,
					tabs = tabs, cont_tag = cont_tag, js = js)

		return VDOM_object.render(self, contents=result)
	
	def wysiwyg(self, contents=""):
	
		object_width = 200
		object_height = 200
		if self.width and self.width > 0:
			object_width = self.width
		if self.height and self.height > 0:
			object_height = self.height
		
		image_id = u"a48a6898-5596-4b88-5864-f82e57f64545"
		result = \
			u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" 
					top="{top}" left="{left}" width="{width}" height="{height}">
					<svg>
						<rect x="{panel_width}" y="0" width="140" height="20" style="stroke:#DDDDDD;stroke-width:1;" fill="#EEEEEE">
							<image x="5" y="0" width="131" height="17" href="#Res({img_id})" />
						</rect>
					</svg>
					<svg>
						<rect x="0" y="20" width="{container_width}" height="{container_height}" style="stroke:#DDDDDD;stroke-width:1;" fill="#EEEEEE"/>
					</svg>{contents}
				</container>
			""".format(
					id = self.id, vis = self.visible, zind = self.zindex, 
					hierarchy = self.hierarchy, top = self.top, left = self.left,
					width = int(object_width) + 2,
					height = int(object_height) + 2, 
					panel_width = int(object_width) - 140,
					container_height = int(object_height) - 20,
					container_width = object_width, 
					img_id = image_id,
					contents = contents)

		return VDOM_object.wysiwyg(self, contents=result)
		
# def set_attr(app_id, object_id, param):
def on_update(object, attributes):
	# obj = application.objects.search(object_id)
	# if "width" in param:
	# 	if param["width"]["value"] and param["width"]["value"] > 0:	
	# 		width = int(param["width"]["value"])
	# 	else:
	# 		width = 200	
	# 	if obj.attributes.width != width:
	# 		obj.set_attribute_ex("width", width)objects
	# if "height" in param:
	# 	if param["height"]["value"] and param["height"]["value"] > 0:	
	# 		height = int(param["height"]["value"])
	# 	else:
	# 		height = 200			
	# 	if obj.attributes.height != height:
	# 		obj.set_attribute_ex("height", height)

	width = attributes.get("width")
	if width is not None:
		width = int(width)
		if width > 0:
			width = str(width - 2)
		else:
			attributes["width"] = width = "200"

	height = attributes.get("height")
	if height is not None:
		height = int(height)
		if height > 0:
			height = str(height - 20)
		else:
			attributes["height"] = height = "200"

	# childs = obj.objects
	# for key in childs:
	for child in object.objects.itervalues():
		# child = childs[key]
		# if obj.attributes.currenttab == child.attributes.hierarchy and str(child.attributes.zindex) != "1":
		# 	child.set_attribute_ex("zindex", "1")
		# elif obj.attributes.currenttab != child.attributes.hierarchy and str(child.attributes.zindex) != "0":
		# 	child.set_attribute_ex("zindex", "0")
		if object.attributes["currenttab"] == child.attributes["hierarchy"] and child.attributes["zindex"] != "1":
			child.attributes.update(zindex="1")
		elif object.attributes["currenttab"] != child.attributes["hierarchy"] and child.attributes["zindex"] != "0":
			child.attributes.update(zindex="0")

		# if "width" in param:
		# 	if param["width"]["value"] and param["width"]["value"] > 0:	
		# 		width = int(param["width"]["value"]) - 2
		# 	else:
		# 		width = 200	
		# 	child.set_attribute_ex("width", width)
		# if "height" in param:
		# 	if param["height"]["value"] and param["height"]["value"] > 0:	
		# 		height = int(param["height"]["value"]) - 20
		# 	else:
		# 		height = 200			
		# 	child.set_attribute_ex("height", height)
		if width is not None:
			child.attributes.update(width=width)
		if height is not None:
			child.attributes.update(height=height)

	css = u""""""
	
	#o = application.objects.search(object_id)
	
	# if "skin" in param:
	# 	if param["skin"]["value"] == "1":
	# 		obj.set_attributes({"style": css})
	# if "style" in param and param["style"]["value"] and obj.attributes.style != css:		
	# 	obj.set_attributes({"skin": 0})
	if attributes.get("skin") == "1":
		attributes["style"] = css

	style = attributes.get("style")
	if style is not None and object.attributes["style"] != css:
		attributes["skin"] = "0"

	# return ""


# def add_child(app_id, object_id, param):
def on_insert(parent, object):
	# object = application.objects.search(param["child_id"])				

	# width_container = int(object.parent.attributes.width) - 2
	# height_container = int(object.parent.attributes.height) - 20
	width_container = int(parent.attributes["width"]) - 2
	height_container = int(parent.attributes["height"]) - 20

	# object.set_attributes({"width": width_container, "height": height_container, "lockposition": "1"})
	object.attributes.update(width=width_container, height=height_container, lockposition="1")

	# childs = object.parent.objects
	container_hierarchy = []
	# for key in childs:
	for child in parent.objects:
		# child = application.objects.search(key)
		# container_hierarchy.append(child.attributes.hierarchy)
		container_hierarchy.append(child.attributes["hierarchy"])

		# if object.parent.attributes.currenttab == child.attributes.hierarchy and str(child.attributes.zindex) != "1":
		# 	child.set_attributes({"zindex": "1"})
		# elif object.parent.attributes.currenttab != child.attributes.hierarchy and str(child.attributes.zindex) != "0":
		# 	child.set_attributes({"zindex": "0"})
		if parent.attributes["currenttab"] == child.attributes["hierarchy"] and child.attributes["zindex"] != "1":
			child.attributes.update(zindex="1")
		elif parent.attributes["currenttab"] != child.attributes["hierarchy"] and child.attributes["zindex"] != "0":
			child.attributes.update(zindex="0")

	# if len(container_hierarchy) > 1 and int(object.attributes.hierarchy) == 0:
	# 	object.set_attributes({"hierarchy": int(max(container_hierarchy)) + 1})
	# 	if object.parent.attributes.currenttab == child.attributes.hierarchy and str(object.attributes.zindex) != "1":
	# 		object.set_attributes({"zindex": "1"})
	# 	elif object.parent.attributes.currenttab != child.attributes.hierarchy and str(object.attributes.zindex) != "0":
	# 		object.set_attributes({"zindex": "0"})
	if len(container_hierarchy) > 1 and int(object.attributes["hierarchy"]) == 0:
		object.attributes.update(hierarchy=str(int(max(container_hierarchy)) + 1))
		if parent.attributes.currenttab == child.attributes.hierarchy and object.attributes["zindex"] != "1":
			object.attributes.update(zindex="1")
		elif parent.attributes.currenttab != child.attributes.hierarchy and object.attributes["zindex"] != "0":
			object.attributes.update(zindex="0")

	# return ""
