
from utils.properties import roproperty
from .properties import render_context_contents_lazy_property, wysiwyg_context_contents_lazy_property


class EngineContext(object):

    def __init__(self, instance):
        self._instance = instance

    instance = roproperty("_instance")


class RenderContext(EngineContext):

    contents = render_context_contents_lazy_property()


class WysiwygContext(EngineContext):

    contents = wysiwyg_context_contents_lazy_property()
