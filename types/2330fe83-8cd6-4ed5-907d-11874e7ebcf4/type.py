
import json
import managers
from scripting import e2vdom


# DOCTYPE = u"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">"""
DOCTYPE = u"""<!DOCTYPE html>"""


JAVASCRIPT = \
    u"<script type='text/javascript' src='/{uuid}.res'></script>" \
    u"<script type='text/javascript'>\n" \
    u"{declarations}\n" \
    u"</script>\n"

JQUERY_UI = \
    u"<link rel='stylesheet' media='screen' type='text/css' href='/eeb5cd9d-2a21-5c85-cd11-f6aed7921730.css'/>" \
    u"<script type='text/javascript' src='/b67cfe82-a508-63ba-37ca-6c27d82c5112.res?v=1.8.20'></script>"

DEFAULT_TEST_FUNCTIONS = "<script type='text/javascript' src='/a81eaffd-b22a-2503-e74e-34b3040c0cd7.res?v20120717'></script>"
DEFAULT_TEST_CLASSES = "<script type='text/javascript' src='/ae073ca4-ab1b-7aec-c8f6-c276b2443a5b.res?v20130417-2'></script>"

CENTERING_CSS = \
    ".center {width: 1100px; margin: 0 auto !important; position: relative;}\n" \
    ".ui-widget-overlay {position: fixed;}"

TEMPLATE = u"""{doctype}
<!--[if lt IE 7]> <html class="is-ie is-ie6 lt-ie7 lt-ie8 lt-ie9 lt-ie10"> <![endif]-->
<!--[if IE 7]>    <html class="is-ie is-ie7 lt-ie8 lt-ie9 lt-ie10"> <![endif]-->
<!--[if IE 8]>    <html class="is-ie is-ie8 lt-ie9 lt-ie10"> <![endif]-->
<!--[if IE 9]>    <html class="is-ie is-ie9 lt-ie10"> <![endif]-->
<!--[if gt IE 9]><!-->
<html>
<!--<![endif]-->
<head>
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1"/>
<meta charset="utf-8"/>
<title>{title}</title>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
{metas}
<script type="text/javascript">
    var APPLICATION_ID="{application}", SESSION_ID="{session}"
    var SERVER_URL="/e2vdom.py"
    var E2VDEBUG={e2vdebug}, E2VSTATE="{e2vstate}", E2VSV={e2vsv};
</script>
<!--[if lte IE 8]><script type="text/javascript" src="/74f3cb60-1736-8714-e09f-f2923263b405.js"></script><![endif]-->
<script type="text/javascript" src="/113513d0-ebae-42c4-9bdf-44ebf7828910.res?v20120118"></script>
{jquery_ui}
{test_functions}
<script type="text/javascript" src="/3e932470-0e08-446c-a866-30c00e6d812a.res"></script>
{test_classes}
<style type="text/css">
{css}
</style>
{static_libraries}
{dynamic_libraries}
<!--[if lt IE 9]><script src="/62bfaaa0-c2fd-02d5-2a32-49056e416a65.res"></script><![endif]-->
</head>
<body id="{element_name}" style="{style}"{inline_style}{inline_class}>
{noscript}
<div id='container'>
{contents}
{javascript}
</div>
<div id='e2vdomindicator' style='z-index:99999;width:1px;height:1px;position:absolute;position:fixed;left:0;top:0;display:none'></div>
<!--[if lt IE 7]>
<script type="text/javascript" src="/0b3e0dc0-6429-eb14-26d6-2d30c535b707.res"></script>
<script type="text/javascript">$j(function(){{ $j('img,input').ifixpng();}});</script>
<![endif]-->
<script type="text/javascript" src="/6cdc7eef-c7d2-bc99-b202-98b2d9052836.res"></script>
<script type="text/javascript">
    hchInit({center},'#{bgcolor}','{id4code}');
    hchSetEvents('{id4code}');
</script>
</body>
<!-- type {type_version}, runtime {server_version} -->
</html>"""


class VDOM_htmlcontainer(VDOM_object):

    def render(self, contents=""):
        if self.visible != "1":
            return VDOM_object.render(self, contents="<html></html>")

        if self.securitycode != "":
            code = str(session["SecurityCode"])
            redirection = not code or code not in self.securitycode.split(";")
            if redirection:
                if self.deniedlink == "":
                    return VDOM_object.render(self, contents="<html></html>")
                else:
                    target = managers.engine.application.objects.catalog.get(self.deniedlink)
                    reference = "/%s.vdom" % target.name if target else ""
                    response.redirect(reference)

        e2vdom.process(self)
        static, dynamic = e2vdom.generate(self)

        static_declarations, static_libraries = static
        dynamic_declarations, dynamic_libraries = dynamic

        javascript_label = "jsdata-%s" % len(static_declarations)
        javascript_resource = application.resources.get_by_label(self.id, javascript_label)
        if javascript_resource:
            javascript_resource_uuid = javascript_resource.id
        else:
            javascript_resource_uuid = application.resources.create_temporary(self.id,
                "jsdata-htmlcontainer", static_declarations.encode("utf-8"), "js", javascript_label)

        javascript = JAVASCRIPT.format(
            declarations=dynamic_declarations,
            uuid=javascript_resource_uuid)

        id4code = self.id.replace('-', '_')
        element_name = u"o_%s" % id4code

        if self.position == "jscenter":
            classname = self.cssclass
            center = "1"
            centering_css = ""
        elif self.position == "center":
            classname = "%s center" % self.cssclass if self.cssclass else "center"
            center = "0"
            centering_css = CENTERING_CSS
        else:
            classname = self.cssclass
            center = "0"
            centering_css = ""

        style = self.style
        style += " margin: 0 auto;"
        if self.bgcolor:
            style += " background-color: #%s;" % self.bgcolor
        style += " color: #%s; font-family: Tahoma; font-size: 12px;" % self.textcolor
        if self.image:
            style += " background-image: url('/%s.res'); background-repeat: %s;" % (self.image, self.bgrepeat)

        inline_style = ""
        if self.linkcolor:
            inline_style += " link=\"#" + self.linkcolor + "\""
        if self.activelinkcolor:
            inline_style += " alink=\"#" + self.activelinkcolor + "\""
        if self.visitedlinkcolor:
            inline_style += " vlink=\"#" + self.visitedlinkcolor + "\""

        metas = u""
        if self.metadescription:
            metas += u'<meta name="description" content="%s" />\n' % (self.metadescription).replace('"', '&quot;')
        if self.metakeywords:
            metas += u'<meta name="keywords" content="%s" />\n' % (self.metakeywords).replace('"', '&quot;')
        if self.customheaders:
            metas += u'%s' % self.customheaders

        if self.noscript:
            noscript = "<noscript>%s</noscript>" % self.noscript
        else:
            noscript = ""

        result = TEMPLATE.format(
            doctype=DOCTYPE,
            type_version=self.type.version,
            server_version=server.version,
            title=self.title.encode("html"),
            metas=metas,
            application=application.id,
            session=session.id,
            e2vdebug="true" if VDOM_CONFIG_1["ENABLE-PAGE-DEBUG"] == "1" else "false",
            e2vstate="0",
            e2vsv=json.dumps(response.shared_variables.copy()),
            jquery_ui=JQUERY_UI,
            test_functions=self.testFunc or DEFAULT_TEST_FUNCTIONS,
            test_classes=self.testClasses or DEFAULT_TEST_CLASSES,
            css="\n".join((self.css, centering_css)),
            static_libraries=static_libraries,
            dynamic_libraries=dynamic_libraries,
            element_name=element_name,
            style=style,
            inline_style=inline_style,
            inline_class=" class='%s'" % classname if classname else "",
            noscript=noscript,
            contents=contents,
            javascript=javascript,
            center=center,
            bgcolor=self.bgcolor,
            id4code=id4code)

        return VDOM_object.render(self, contents=result)

    def wysiwyg(self, contents=""):
        result = "<container id=\"%s\" visible=\"%s\" zindex=\"%s\" hierarchy=\"%s\" order=\"%s\" backgroundcolor=\"#%s\" backgroundimage=\"%s\" backgroundrepeat=\"%s\" >%s</container>" % (
            self.id, self.visible, self.zindex, self.hierarchy, self.order, self.bgcolor, self.image, self.bgrepeat, contents)
        return VDOM_object.wysiwyg(self, contents=result)
