
class RenderContextContentsLazyProperty(object):

    def __get__(self, instance, owner=None):
        instance._instance.execute()
        instance.contents = value = instance._instance.render()
        return value


class WysiwygContextContentsLazyProperty(object):

    def __get__(self, instance, owner=None):
        instance.contents = value = instance._instance.wysiwyg()
        return value


render_context_contents_lazy_property = RenderContextContentsLazyProperty
wysiwyg_context_contents_lazy_property = WysiwygContextContentsLazyProperty
