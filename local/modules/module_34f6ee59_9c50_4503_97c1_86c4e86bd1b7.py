# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request
from scripting import e2vdom


class VDOM_form(VDOM_object):

	def render(self, contents=""):
		display = u"display:none; " if self.visible == "0" else u""
		
		e2vdom.process(self)

		if self.overflow == "1":
			ov = u"hidden"
		elif self.overflow == "2":
			ov = u"scroll"
		elif self.overflow == "3":
			ov = u"visible"
		else:
			ov = u"auto"

		if not self.target or self.meth == "event":
			target = u""
		else:
			ref_obj = application.objects.search(self.target)
			target = u"/%s.vdom" % ref_obj.name if ref_obj else u""

		submitonce = u""

		woid = (self.id).replace('-', '_')
		id = u"o_" + woid

		if self.meth == "event":
			submitjs = u"""<script type="text/javascript">
$j(function(){
  $j('#%(id)s').submit(function(e){
    
    var $form = $j(this);

    if ($j('body').data('%(id)s_submitted') == '1')
      return false;
    
    $j('body').data('%(id)s_submitted', '1');
    setTimeout(function() {
      $j('body').data('%(id)s_submitted', '');
    }, 1000);

    var formData = {};

    var submitTrigger = $form.children('input[name=__submit_trigger__]');
    if (submitTrigger.length){
      formData[submitTrigger.val()] = 1;
      submitTrigger.remove();
    }
    
    var a = $j('#%(id)s').serializeArray();
    for (k in a){
      if(typeof a[k].name !== 'undefined' && typeof a[k].value !== 'undefined') {
        if (formData.hasOwnProperty(a[k].name)){
          if (jQuery.isArray(formData[a[k].name])){
            formData[a[k].name].push(a[k].value);
          } else {
            v = formData[a[k].name];
            formData[a[k].name] = new Array(v, a[k].value);
          }
        } else {
          formData[a[k].name]=a[k].value;
        }
      }
    }
    execEventBinded('%(woid)s', "submit", formData);
    return false;
  });

  $j('#%(id)s input[type=submit]').click(function(){
    var form = $('#%(id)s');
    if (!form.children('input[name=__submit_trigger__]').length){
      form.append('<input type="hidden" name="__submit_trigger__" value="' + $(this).attr('name') + '" />');
    } else {
      form.children('input[name=__submit_trigger__]').val($(this).attr('name'));
    }
  });
});
</script>""" % { "id": id, "woid": woid }
		else:
			submitjs = u""

		if not self.enctype or self.meth == "event":
			enctype = u""
		else:
			enctype = u"""enctype="%s" """ % self.enctype

		style = u"overflow:{ovf};z-index:{zind};position:{pos};top:{top}px;left:{left}px;width:{wid}px;height:{hei}px;" \
			.format(ovf = ov, zind = self.zindex, pos = self.position, 
					top = self.top, left = self.left, wid = self.width, hei = self.height)

		classname = u"""class="%s" """ % self.classname if self.classname else u""

		if VDOM_CONFIG_1["DEBUG"] == "1":
			debug_info = u"objtype='form' objname='%s' ver='%s'" % (self.name, self.type.version)
		else:
			debug_info = u""

		result = \
			u"""<form {debug_info} id="{id}" style="display:block;margin:0; {display} {style}" 
					name="{name}" method="{method}" action="{target}" style="overflow:visible" 
					{enctype} {submitonce} {classname}>
					{contents}
				</form> {submitjs} 
			""".format(
					debug_info = debug_info, id = id, display = display, style = style, name = self.name, 
					method = self.meth, target = target, enctype = enctype, submitonce = submitonce, 
					contents = contents, submitjs = submitjs, classname = classname )

		return VDOM_object.render(self, contents=result)

	def wysiwyg(self, contents=""):
		if len(contents) == 0:
			import utils.wysiwyg
			
			image_id = "54e7f8ab-64f1-b113-029e-1703a76c6fa4"
			result = utils.wysiwyg.get_empty_wysiwyg_value(self, image_id)
			
			return VDOM_object.wysiwyg(self, contents=result)
		
		# get overflow value
		overflow_dict = {"0":"auto", "1":"hidden", "2":"scroll", "3":"visible"}
		overflow_num = self.overflow if self.overflow else "0"
		overflow = overflow_dict[overflow_num]
			
		result = u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
							top="{top}" left="{left}" width="{width}" height="{height}" overflow="{overflow}">
						<svg>
							<rect x="0" y="0" width="{width}" height="{height}" fill="#EEEEEE" fill-opacity=".4" />
						</svg>{contents}
					</container>
				""".format(id = self.id, vis = self.visible, zind = self.zindex, 
				hierarchy = self.hierarchy, order = self.order, 
				top = self.top, left = self.left, width = self.width, height = self.height, 
				contents = contents,
				overflow = overflow)
		
		return VDOM_object.wysiwyg(self, contents=result)

		
