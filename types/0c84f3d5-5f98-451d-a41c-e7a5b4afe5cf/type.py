
import json
import StringIO

from collections import OrderedDict, Iterable
from itertools import izip


class VDOM_formlist(VDOM_object):

    def get_data(self):
        # try to parse json
        try:
            value = json.loads(self.value, object_pairs_hook=OrderedDict)

        except Exception:
            if self.value:
                raise Exception(u"value: %r. Incorrect format of JSON data" % self.value)

            value = []

        if not isinstance(value, Iterable):
            raise Exception(u"value: %r. Must be dict or list" % self.value)

        return value
            
    def render(self, contents=""):
        display = u"display:none; " if self.visible == "0" else u""

        style = u"""{display}position: absolute; z-index: {zind}; top: {top}px; left: {left}px; width: {width}px; height: {height}px; font: 14px tahoma""".format(
            zind = self.zindex,
            top = self.top,
            left = self.left, 
            width = self.width,
            height = self.height,
            display = display
        )

        id = u"o_" + (self.id).replace('-', '_')
        
        disabled = u""" disabled="disabled\"""" if self.disabled == "1" else u""
        multi = u""" multiple="multiple\"""" if self.multiselect and self.multiselect == "1" else u""
        size = u""" size="%s" """ % self.size if self.size else u""

        select = u"""<select id="{id}" name="{name}" tabindex="{tabind}" autocomplete="off" style="{style}" {size}{multi}{disabled}>""".format(
            disabled = disabled,
            id = id,
            name = self.name,
            tabind = self.tabindex,
            style = style,
            size = size,
            multi = multi,
        )

        try:
            selected_values = json.loads(self.selectedvalue)
        except:
            selected_values = self.selectedvalue

        if not isinstance(selected_values, list):
            selected_values = [selected_values]

        try:
            disabled_values = json.loads(self.disabledvalue)
        except:
            disabled_values = self.disabledvalue

        if not isinstance(disabled_values, list):
            disabled_values = [disabled_values]

        data = self.get_data()
        try:
            data = data.iteritems()
        except:
            data = izip(xrange(len(data)), data)

        result = u"".join([u"""<option value="{value}"{selected}{disabled}>{title}</option>""".format(
            value=value,
            selected=u""" selected="selected\"""" if value in selected_values else u"",
            disabled=u""" disabled="disabled\"""" if value in disabled_values else u"",
            title=title
        ) for value, title in data])

        result = u"{}{}</select>".format(select, result)
        return VDOM_object.render(self, contents=result)
    
    def wysiwyg(self, contents=""):
        
        rect_width = int(self.width)-1 if int(self.width)>1 else int(self.width)
        rect_height = int(self.height)-1 if int(self.height)>1 else int(self.height)
        
        btn_width = 15 if rect_width > 15 else rect_width
        btn_height = rect_height
        btn_y = 0
        btn_x = rect_width - btn_width - 1 if rect_width > btn_width else 0
        
        triangle_width = 5 
        if btn_width < triangle_width :
            triangle_width = btn_width
            triangle_x = btn_x
        else :
            triangle_x = btn_x + (btn_width - triangle_width) / 2 + 1
            
        triangle_height = 4 
        if btn_height < triangle_height :
            triangle_height = btn_height
            triangle_y = 0
        else :
            triangle_y = (btn_height - triangle_height) / 2
        
        color = "#aaaaaa" if self.disabled=="1" else "#000000"
        btn = \
                u"""<svg>
                        <rect x="{btn_x}" y="{btn_y}" width="{btn_width}" height="{btn_height}" fill="#EEEEEE" stroke="{color}"/>
                        <polygon fill="{color}" stroke="{color}" points="{xa},{ya} {xb},{yb} {xc},{yc}"/>
                    </svg>
                """.format(btn_x = btn_x, btn_y = btn_y,
                            btn_width = btn_width, btn_height = btn_height,
                            xa = triangle_x, ya = triangle_y,
                            xb = triangle_x+triangle_width, yb = triangle_y,
                            xc = triangle_x+triangle_width/2, yc = triangle_y+triangle_height,
                            color = color)
        
        result = \
            u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}" 
                        top="{top}" left="{left}" width="{width}" height="{height}">
                    <svg>
                        <rect y="0" x="0" width="{rect_width}" height="{rect_height}" fill="#FFFFFF" stroke="{color}"/>
                    </svg>
                    <svg>
                        <text x="{text_x}" y="{text_y}" width="{width}" height="{height}" fill="{color}" font-size="14" font-family="tahoma"></text>
                    </svg>
                    {btn}
                </container>
            """.format(id = self.id, vis = self.visible, zind = self.zindex, 
                    hierarchy = self.hierarchy, order = self.order, 
                    top = self.top, left = self.left, 
                    width = self.width, height = self.height,
                    rect_width = rect_width, rect_height = rect_height, 
                    btn = btn,
                    text_x = 7,
                    text_y = 15 if rect_height < 15 else (rect_height-15)/2+15,
                    color = color)
        

        return VDOM_object.wysiwyg(self, contents=result)

	
