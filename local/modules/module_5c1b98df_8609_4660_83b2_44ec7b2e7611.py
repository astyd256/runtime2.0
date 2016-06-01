# coding=utf8

from scripting import server, application, log, session, request, response, VDOM_object, obsolete_request


def on_startup(object):
    source_object = object.application.objects.get(object.attributes["source_object"])
    if source_object:
        source_object.attach(object)


def on_create(object):
    source_object = object.application.objects.get(object.attributes["source_object"])
    if source_object:
        source_object.attach(object)


def on_delete(object):
    source_object = object.application.objects.get(object.attributes["source_object"])
    if source_object:
        source_object.detach(object)


def on_update(object, attributes):
    if "source_object" in attributes:
        source_object = object.application.objects.get(object.attributes["source_object"])
        if source_object:
            source_object.detach(object)
        source_object = object.application.objects.get(attributes["source_object"])
        if source_object:
            source_object.attach(object)


def on_render(self, child):
    if self.top != "":
        child.top = self.top
    if self.left != "":
        child.left = self.left


def on_wysiwyg(self, child):
    child.top = 0
    child.left = 0


def on_compile(object, profile):
    source_object = object.application.objects.catalog.get(object.attributes["source_object"])
    if source_object:
        profile.dynamic = 1
        profile.optimization_priority = source_object.type.optimization_priority
        profile.entries.new(source_object, on_render=on_render, on_wysiwyg=on_wysiwyg)


class VDOM_copy(VDOM_object):

    def check_cache(self):
        if self.source_object_cache != self.source_object:
            # reset copy position
            self.source_object_cache = self.source_object
            self.top = ""
            self.left = ""
            self.update("source_object_cache", "top", "left")

    def render(self, contents=""):
        self.check_cache()
        result = contents if self.visible == "1" else u""
        return VDOM_object.render(self, contents=result)

    def empty_copy(self):
        from scripting.utils.wysiwyg import get_centered_image_metrics
        top = self.top if self.top else 10
        left = self.left if self.left else 10
        width = 100
        height = 100

        image_id = "4d6060c5-5acd-bd35-8f4c-0888ae0306f0"
        image_x = image_y = 0
        image_width = image_height = 50

        image_x, image_y, image_width, image_height = get_centered_image_metrics(image_width, image_height, width, height)

        designcolorvalue = u"#" + self.designcolor if self.designcolor != "" else "none"

        result = \
            u"""<container id="{id}" visible="{vis}" zindex="{zind}" hierarchy="{hierarchy}" order="{order}"
                    top="{top}" left="{left}" width="{width}" height="{height}"
                    backgroundcolor="#EEEEEE" contents="static">
                    <svg>
                        <rect x="0" y="0" width="{width}" height="{height}" fill="{designcolorvalue}"/>
                        <image href="#Res({image_id})" x="{image_x}" y="{image_y}" width="{image_width}" height="{image_height}" />
                    </svg>
                </container>
            """.format(
                id=self.id,
                vis=self.visible,
                zind=self.zindex,
                hierarchy=self.hierarchy,
                order=self.order,
                designcolorvalue=designcolorvalue,
                top=top,
                left=left,
                width=width,
                height=height,
                image_id=image_id,
                image_width=image_width,
                image_height=image_height,
                image_x=image_x,
                image_y=image_y)
        return result

    def wysiwyg(self, contents=""):
        self.check_cache()

        designcolorvalue = u"#" + self.designcolor if self.designcolor != "" else "none"

        if self.source_object:
            object = application.objects.search(self.source_object)

            if object:
                top = self.top if self.top else object.get_attributes()["top"].value
                left = self.left if self.left else object.get_attributes()["left"].value
                width = object.get_attributes()["width"].value

                height1 = height2 = u""
                if "height" in object.get_attributes():
                    height = object.get_attributes()["height"].value
                    height1 = u"""height="%s" """ % height
                    height2 = u"""height="%s" """ % str(int(height) + 2)

                zindex = self.zindex
                if "zindex" in object.get_attributes():
                    zindex = object.get_attributes()["zindex"].value

                result = \
                    u"""<container id="{id}" visible="{vis}" zindex="{zind}"
                            top="{top}" left="{left}" width="{width2}" {height2} contents="static">
                            <svg>
                                <rect x="0" y="0" width="{width2}" {height2} fill="{designcolorvalue}"/>
                            </svg>
                            <container top="1" left="1" width="{width}" {height1} contents="static">
                                {contents}
                            </container>
                        </container>
                    """.format(
                        id=self.id,
                        vis=self.visible,
                        zind=zindex,
                        designcolorvalue=designcolorvalue,
                        width2=str(int(width) + 2),
                        height2=height2,
                        top=top,
                        left=left,
                        width=width,
                        height1=height1,
                        contents=contents)
            else:
                result = self.empty_copy()
        else:
            result = self.empty_copy()

        return VDOM_object.wysiwyg(self, contents=result)
