
class VDOM_formcheckbox(VDOM_object):

  def render(self, contents=""):
    display = u" display: none; " if self.visible == "0" else u""
    weight = u" bold " if self.fontweight == "bold" else u""
    disable = u"disabled='disabled'" if self.disable == "1" else u""
    
    state = [u"", u"""checked="checked" """][int(self.attributes["state"])]
    style = u"""overflow: hidden; z-index: {zind}; position: {pos}; top: {top}px; left: {left}px; 
          width: {width}px; height: {height}px; font: {weight} {size}px tahoma;{display} 
        """.format(zind = self.zindex, pos = self.position, top = self.top, left = self.left,
            width = self.width, height = self.height, weight = weight, size = self.fontsize, display = display)
    
    clean_id = (self.id).replace('-', '_')
    id = u"o_" + clean_id

    result = u"""<div id="%(id)s" style="%(style)s">
            <input name="%(name)s" type="checkbox" %(state)s tabindex="%(tabind)s" value="%(value)s" 
              id="inp_%(id)s" style="vertical-align:top;#vertical-align:middle" %(disable)s/> 
            <label for="inp_%(id)s" style="vertical-align:middle">%(label)s</label>
            %(contents)s
          </div>
          <script type="text/javascript">jQuery(document).ready(function($){
$('#inp_%(id)s').click(function(){
  var v = ($(this).is(':checked')) ? "1" : "0";
  execEventBinded('%(clean_id)s', 'change', { "Value": v });
  execEventBinded('%(clean_id)s', v == "1" ? 'checked' : 'unchecked', { "value": v })
});
          });</script>
        """ % {"id": id, "style": style, "name": self.name, "state": state, 
            "tabind": self.tabindex, "value": self.value, "disable": disable,"label": self.label, 
            "contents": contents, "clean_id": clean_id}

    return VDOM_object.render(self, contents=result)

  def wysiwyg(self, contents=""):
    fontsize = u" {fsize}px ".format(fsize = self.fontsize) if self.fontsize else u" "
    state = [u"", u""" checked="checked" """][int(self.state)]
    disable = u""" disabled="disabled" """ if self.disable == "1" else u""
    
    result = \
      u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
            top="{top}" left="{left}" width="{width}" height="{height}" >
          <htmltext top="0" left="0" width="{width}" height="{height}" locked="true" overflow="hidden">
            <input type="checkbox" {state} {disable}
                  style="vertical-align:top; font: {fontweight} {fontsize} tahoma;" /> 
            <label style="vertical-align:middle; font: {fontweight} {fontsize} tahoma;">{label}</label>
            
          </htmltext>
        </container>
      """.format(
        id = self.id, vis = self.visible, zind = self.zindex, 
        hierarchy = self.hierarchy, order = self.order, 
        top = self.top, left = self.left, width = self.width, height = self.height,
        label=self.label,
        fontsize = fontsize,
        fontweight = self.fontweight,
        state = state,
        disable = disable)

    return VDOM_object.wysiwyg(self, contents=result)

		
