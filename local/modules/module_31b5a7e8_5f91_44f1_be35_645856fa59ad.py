# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request



import collections
import json


CLICK_N_SELECT = (
  "click",
  "ctrlclick",
  "dblclick",
  "ctrldblclick",
  "manual",
)


class VDOM_listv2(VDOM_object):

    def parse_property(self, pname, ptype, *args, **kwargs):
        prop = getattr(self, pname)
        if not prop:
            return ptype()

        try:
            value = json.loads(prop, *args, **kwargs)

        except Exception as ex:
            if prop:
                raise Exception(u"Can't parse '%s'. It must be '%s'" % (pname, ptype.__name__))

            value = ptype()

        return value

    def render(self, contents=""):

        obj_id = self.id.replace('-', '_')

        items = self.parse_property("data", dict, object_pairs_hook=collections.OrderedDict)
        selected_rows = self.parse_property("selectedrows", list)
        selectable_rows = self.parse_property("selectablerows", list)
        droppable_rows = self.parse_property("droppablerows", list)
        active_row = self.activeitem
        multi_selection = True if self.selectionmode == "1" else False
        already_selected = False

        # compatibility with old version
        can_be_droppable = False
        if self.droppable == "1":
            if not droppable_rows:
                can_be_droppable = True

        can_be_selectable = False
        if not selectable_rows:
            can_be_selectable = True

        result = []
        index = 1
        is_first = True

        for key, value in items.iteritems():
            
            css_class = u"list-item-{index}{is_first}{is_last}{is_odd}{is_active}{is_selected}{is_selectable}{is_droppable}".format(
                index=index,
                is_first=" list-item-first" if is_first else "",
                is_last=" list-item-last" if index == len(items) else "",
                is_odd=" list-item-odd" if index % 2 == 0 else "",
                is_active=u" active" if active_row == key else u"",
                is_selected=u" selected" if key in selected_rows and not already_selected else u"",
                is_selectable=u" selectable" if key in selectable_rows or can_be_selectable else u"",
                is_droppable=u" droppable" if key in droppable_rows or can_be_droppable else u""
            )

            result.append(u"""<li itemid="{key}" class="{css_class}">{content}</li>""".format(
                key=key,
                css_class=css_class,
                content=value
            ))

            if not multi_selection and key in selected_rows:
              already_selected = True

            index += 1
            is_first = False

        options = {
          "droppable": self.droppable == "1",
          "clickClasses": self.clickclass.strip().split(),
        }

        output = u"""<div id="o_{id}" name="{name}" objtype="listv2" ver="{version}" style="{display};z-index: {zindex};position: absolute;top: {top}px;"""\
        """left: {left}px;height: {height}px;width: {width}px" class="{css_class}" selectionmode="{selectionmode}" select-on-click="{selectonclick}">
    <ul>
        {content}
    </ul>
</div>
<style type="text/css">
#o_{id} ul {{
  list-style: none outside none;
  margin: 0;
  padding: 0;
}}
#o_{id} ul li {{
  display: {item_display};
}}
{css}
</style>
<script type="text/javascript">jQuery(document).ready(function(){{jQuery("#o_{id}").vdomList_v2({options});}});</script>""" 

        contents += output.format(
            version=self.type.version,
            name=self.name,
            css_class=self.classname,
            content="".join(result),
            id=obj_id,
            css=self.style % {"id": "o_" + obj_id},
            display=u"display:none;" if self.visible == "0" else u"",
            zindex=self.zindex,
            top=self.top,
            left=self.left,
            height=self.height,
            width=self.width,
            item_display="inline" if self.layout == "1" else "list-item",
            options=json.dumps(options),
            selectionmode="multiselection" if multi_selection else "singleselection",
            selectonclick=CLICK_N_SELECT[int(self.selectonclick)],
        )

        return VDOM_object.render(self, contents=contents)        
            
    def wysiwyg(self, contents=""):
        from scripting.utils.wysiwyg import get_empty_wysiwyg_value
        image_id = "e1246b00-381e-4b32-bad7-4a647a08d557"
        result = get_empty_wysiwyg_value(self, image_id)
        return VDOM_object.wysiwyg(self, contents=result)

  
