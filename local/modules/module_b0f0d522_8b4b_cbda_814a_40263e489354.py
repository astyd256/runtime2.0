# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request

from scripting import e2vdom
import managers
import json
import collections

from uuid import uuid4


JS_DRAG = u"""
$j("#%(id)s div[dataid]").liveDraggable({
    connectToDynatree: true,
    appendTo: 'body',
    containment: 'document',
    zIndex: 99999,
    /*option: 'accept',*/
    cursor: 'default',
    cursorAt: { left: -2, top: 4 },
    start: function(e,u){
        execEventBinded('%(woid)s', "dragstart", {id: $j(this).attr('dataid')}, true);
    },
    connectToSortable: '#%(id)s',
    revert: "invalid",
    revertDuration: 200,
    /*helper: 'clone'*/
    opacity: 1,
    helper: function(e) {
        return $j("<div class='ov-drag-helper' style='width:50px;height:20px;background:#555'></div>");
    }
});
/*
$('#%(id)s').droppable({
    disabled: true,
    accept: ".nobody",
    drop: function(event, ui){
        type = ui.draggable.find('.link_type').val();
        ui.draggable.empty();
        //return ui.draggable.html(create(type,0))
        return ui.draggable;
    }
});
*/
"""

JS_SORTABLE = u"""
$j('#%(id)s').liveSortable({
    items: 'div[dataid]',
    receive: function (event, ui){
        ui.item.remove();
        //ui.sender.remove();
    },
    stop: function(e, u) {
        execEventBinded('%(woid)s', "itemsort", {position: u.item.index(), id: u.item.attr('dataid')});
    }
}).disableSelection();
/*}).disableSelection().bind("sortstop",function(e,u){
    execEventBinded('%(woid)s', "itemsort", {position: u.item.index(), id: u.item.attr('dataid')});
    //ui.draggable.empty();
    //return ui.draggable;
});*/
"""

JS_LOADING = u"""
%(id)s_ld = function(t){
    var z = $j('>.loading',t);
    if (z.size() > 0) {
        if (z.is(':visible')) return;
        z.fadeIn(100);
    } else {
        var x = $j('<div class="loading" style="width:100%%;height:100%%"></div>').css({position:'absolute',opacity:0.9}).hide().fadeIn(100);
        t.append(x);
    }
    e2vdomAfterResponse('$j("#%(id)s>div.ov-content>div[dataid='+t.attr('dataid')+']>.loading").fadeOut(100);');
}
"""

JS_DYNAMIC = u"""
    $j("#%(id)s").bind('scrollstop resize', function() {
        var obj = $j("#%(id)s");
        var $content = $('>div.ov-content', obj);
        var canLoadContent = $content.outerHeight() - obj.innerHeight() - obj.scrollTop() <= 30;
        if (canLoadContent) {
            execEventBinded("%(woid)s", 'endscroll', {});
        }
        vdom_ov_markShow("%(woid)s");
    });
    vdom_ov_markShow("%(woid)s");
    window.setTimeout('vdom_ov_markShow("%(woid)s")', 2000);
"""

JS = u"""<style type='text/css'>
#%(id)s .loading { background: #fff url('/1869b90e-c056-1337-dfac-72b9873df6fa.res') center center no-repeat; }
#%(id)s .not-loaded { background: url('/feb69c13-3f9b-f49f-6527-72f5a7193a34.res') center center no-repeat; }
</style>
<script type="text/javascript">
%(js_loading)s

$j(function(){
    $j("#%(id)s").data("ovitemclass","%(class)s-item");

    $j("#%(id)s div[dataid]").live('click dblclick', function(e){
        if (e.preventDefault) e.preventDefault(); else e.returnValue = false;
        var t = $j(this);
        if (e.type == 'dblclick') {
            t.data('doo', false);
            %(js_loading_call)s
            execEventBinded('%(woid)s', "itemdblclick", {"id":t.attr("dataid")});
            return false;
        } else {
            setTimeout(function() {
                if (t.data('doo') == true) {
                    %(js_loading_call)s
                    execEventBinded('%(woid)s', "itemclick", {"id":t.attr("dataid")});
                    return false;
                }
            }, 220);
            t.data('doo', true);
        }
        return false;
    });

    $j("#%(id)s div[dataid]").live('mouseover', function(e){
        execEventBinded('%(woid)s', "itemmouseover", {"id":$j(this).attr("dataid"), 'X':e.pageX, 'Y':e.pageY});
        return false;
    }).live('mouseout', function(e){
        execEventBinded('%(woid)s', "itemmouseout", {"id":$j(this).attr("dataid")});
        return false;
    });

    %(js_sortable)s
    %(js_drag)s
    %(js_dynamic)s

});
</script>"""

JS_INFINITE_SCROLL = u"""
$j('#%(id)s').infiniteScroll({
    'ovid': '%(woid)s',
    'cssc': '%(cssc)s'
});
/*
var obj = $j("#%(id)s");
var $content = $('>div.ov-content', obj);
var canLoadContent = $content.outerHeight() - obj.innerHeight() - obj.scrollTop() <= 30;
if (canLoadContent) {
    execEventBinded("%(woid)s", 'itemsrequestforinfinite', { loaded: $('>div.ov-content>div[dataid]',obj).size() });
}
*/
"""


E2VDOM_DYNAMIC_JAVASCRIPT = u"""
var x = $j('#%(id)s>div.ov-content');
$j('>div[dataid]', x).remove();
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    $j(">span.ov-eoi", x).before( $j('>div[dataid]', ovtmp) );
}
"""

E2VDOM_DIV_ONLY_JAVASCRIPT = u"""
var x = $j('#%(id)s>div.ov-content');
$j('>div[dataid]', x).remove();
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    $j(">span.ov-eoi", x).before( $j('>div[dataid]', ovtmp) );
    /*$j('>div[dataid]',ovtmp).each(function(){
        $j(">span.ov-eoi", x).before($j(this));
    });*/
    vdom_ov_markShow("%(woid)s");
}
"""

E2VDOM_RENDER_JAVASCRIPT = u"""
var ovtmp = $j('#%(tmp_id)s:last');
if ($j.trim(ovtmp.html()) != '') {
    var x = $j('#%(id)s>div.ov-content');
    $j('>div[dataid]',ovtmp).each(function(){
        var t = $j(this);
        var i = $j(">div[dataid="+t.attr('dataid')+"]", x);
        if (i.size() > 0) {
            if (i.hasClass('selected')) t.addClass('selected');
            i.before(t);
            i.remove();
            //} else {
            //  $j(">span.ov-eoi", x).before($j(this));
        }
    });
    vdom_ov_markShow("%(woid)s");
}
"""


class VDOM_objectview(VDOM_object):

    def render_items(self, items, div_only):
        if not self.vdomclassid:
            return ""

        classname = self.classname or u"ov"
        source_object = application.objects.search(self.vdomclassid)

        if not source_object:
            return u"Invalid VDOM class"

        width = source_object.attributes["width"]
        height = source_object.attributes["height"]

        if not div_only:
            object_to_render = application.objects.search(self.id)

        last_index = len(items) - 1
        result = ""
        for index, key in enumerate(items):
            copy = managers.engine.application.objects.new(source_object.type,
                name="vdomclass%d" % index, virtual=True, attributes=source_object.attributes)
            copy.objects += source_object.objects
            copy.actions += source_object.actions

            classes = " ".join(filter(None,
                (
                    u"%s-item" % classname,
                    u"%s-item-%s" % (classname, index + 1),
                    (u"%s-item-first" % classname) if index == 0 else None,
                    (u"%s-item-last" % classname) if index == last_index else None,
                    (u"%s-item-odd" % classname) if index % 2 else None,
                    u"not-loaded" if div_only else None
                )))

            copy.attributes.update(
                {
                    "data": items[key],
                    "dataid": key,
                    "visible": "1",
                    "width": width,
                    "height": height,
                    "classauto": classes,
                    "classname": source_object.attributes["classname"]
                })

            if div_only:
                result += u"""<div class="{classes}" dataid="{id}" style="{style}"></div>""".format(
                    id=key,
                    classes=classes,
                    style=u"position:relative;width:%spx;height:%spx;display:block;" % (width, height))
            else:
                result += managers.engine.render(copy, object_to_render, "vdom")

        return result

    def render(self, contents=""):
        woid = (self.id).replace('-', '_')
        id4js = u"o_" + woid

        try:
            items = json.loads(self.data, object_pairs_hook=collections.OrderedDict)
            if isinstance(items, list):
                # if not items:
                #     items.append("dummy-item-554f180b-1c2a-6705-3608-87f71366710b")
                items = collections.OrderedDict((unicode(key), "") for key in items)
                div_only = True
            else:
                div_only = False
        except:
            items = {}
            div_only = False

        items_contents = self.render_items(items, div_only)

        if request.render_type == "e2vdom":
            # action render
            tmp_id = u"ov%s" % uuid4()
            if self.dynamicrender == "0":
                js = E2VDOM_DYNAMIC_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}
            else:
                if div_only:   # [] - empty frames: rerender
                    js = E2VDOM_DIV_ONLY_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}
                else:         # {} - items with content: render items in empty frames
                    js = E2VDOM_RENDER_JAVASCRIPT % {"id": id4js, "tmp_id": tmp_id, "woid": woid}

            return VDOM_object.render(self, contents=u"""<noreplace/>
<div id="%(tmp_id)s" style="display:none">%(contents)s</div>
<script type='text/javascript'>
    %(js)s
</script>""" % {"js": js, "contents": items_contents, "tmp_id": tmp_id})
        else:
            # initial render
            e2vdom.process(self, self.parent.id if self.parent else None)

            if self.overflow == "1":
                overflow = u"hidden"
            elif self.overflow == "2":
                overflow = u"scroll"
            elif self.overflow == "3":
                overflow = u"visible"
            else:
                overflow = u"auto"

            classes = (
                u"display:none;" if self.visible == "0" else None,
                u"z-index: {zindex}; position: {pos}; top: {top}px; left: {left}px; "
                "width: {width}px; height: %spx; overflow: {overflow};".format(
                    zindex=self.zindex,
                    pos=self.position,
                    top=self.top,
                    left=self.left,
                    width=self.width,
                    height=self.height,
                    overflow=overflow)
            )
            style = " ".join(filter(None, classes))

            classname = u"""class="%s" """ % self.classname if self.classname else u""

            classname_item = 'ov' if self.classname == '' else (self.classname).replace(' ', '')

            # items layout

            if self.layout == "1":
                layout = u"float: left;"
            elif self.layout == "0":
                layout = u"clear: both;"
            else:
                layout = u"width: 100% !important; clear: both;"

            style_items = u"""<style type="text/css">
#%(id)s .%(class)s-item {
%(layout)s
}
</style>""" % {"id": id4js, "class": classname_item, "layout": layout}

            if self.loading == "0":
                js_loading_call = u""
                js_loading = u""
            else:
                js_loading_call = u"%s_ld(t);" % id4js
                js_loading = JS_LOADING % {"id": id4js}

            js_dynamic = JS_DYNAMIC % {"id": id4js, "woid": woid, "cssc": classname_item}

            js_drag = JS_DRAG % {"id": id4js, "woid": woid, "class": classname_item} if self.draggable == "1" else ""

            js_sortable = JS_SORTABLE % {"id": id4js, "woid": woid} if self.sortable == "1" else ""

            js = JS % {
                "js_drag": js_drag,
                "id": id4js,
                "woid": woid,
                "class": classname_item,
                "js_loading": js_loading,
                "js_loading_call": js_loading_call,
                "js_dynamic": js_dynamic,
                "js_sortable": js_sortable
            }

            if VDOM_CONFIG_1["DEBUG"] == "1":
                debug_info = u"objtype='objectview' objname='%s' ver='%s'" % (self.name, self.type.version)
            else:
                debug_info = u""

            result = u"""
                <div {debug_info} id="{id}" style="{style}" {classname}>
                    {style_items}
                    <div class='ov-content'>
                        {contents}
                        <span class='ov-eoi' style='display:block;clear:both'></span>
                    </div>
                </div>
                {js}
                """.format(
                js=js,
                id=id4js,
                debug_info=debug_info,
                style=style,
                style_items=style_items,
                classname=classname,
                contents=items_contents
            )

            return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        from scripting.utils import wysiwyg
        result = wysiwyg.get_empty_wysiwyg_value(self, "cc72f740-5527-4dab-3c59-16b7fccb0032")
        return VDOM_object.wysiwyg(self, contents=result)
