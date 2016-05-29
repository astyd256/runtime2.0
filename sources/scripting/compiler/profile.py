
from collections import Sequence
from logs import log
from utils.properties import roproperty, rwproperty


class CompilationProfileEntity(object):

    def __init__(self, origin, context):
        self._origin = origin
        self._context = context

        self._stateful = origin.stateful
        self._hierarchy = origin.hierarchy

    origin = roproperty("_origin")
    context = roproperty("_context")

    stateful = roproperty("_stateful")
    hierarchy = roproperty("_hierarchy")


class CompilationProfileEntry(CompilationProfileEntity):

    def __init__(self, origin, context, on_initialize, on_execute, on_render, on_wysiwyg):
        super(CompilationProfileEntry, self).__init__(origin, context)

        self._klass = origin.factory(context)  # also need to calculate dynamic

        self._dynamic = self._klass._dynamic
        self._optimization_priority = self._klass._optimization_priority

        self._on_initialize = on_initialize
        self._on_execute = on_execute
        self._on_render = on_render
        self._on_wysiwyg = on_wysiwyg

    klass = roproperty("_klass")

    dynamic = roproperty("_dynamic")
    optimization_priority = roproperty("_optimization_priority")

    on_initialize = rwproperty("_on_initialize")
    on_execute = rwproperty("_on_execute")
    on_render = rwproperty("_on_render")
    on_wysiwyg = rwproperty("_on_wysiwyg")


class CompilationProfileEntries(Sequence):

    def __init__(self, profile):
        self._profile = profile
        self._items = []

    def new(self, origin, on_initialize=None, on_execute=None, on_render=None, on_wysiwyg=None):
        item = CompilationProfileEntry(origin, self._profile.context,
            on_initialize, on_execute, on_render, on_wysiwyg)
        self._items.append(item)
        return item

    def _finalize(self):
        self._items.sort(key=lambda item: (item.hierarchy, item.optimization_priority))

    def clear(self):
        self._items = []

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._entries)


class CompilationProfile(CompilationProfileEntity):

    def __init__(self, origin, context, dynamic=None):
        super(CompilationProfile, self).__init__(origin, context)

        self._dynamic = dynamic or origin.type.dynamic
        self._optimization_priority = origin.type.optimization_priority

        self._action = origin.actions.get(context)
        self._class_name = "%s_%s" % (origin.type.class_name, origin.id.replace("-", "_"))
        self._entries = CompilationProfileEntries(self)

    def __enter__(self):
        for child in self._origin.objects.itervalues():
            self._entries.new(child)
        return self

    def __exit__(self, extype, exvalue, extraceback):
        if not extype:
            self._finalize()

    def _set_dynamic(self, value):
        if value < self._dynamic:
            raise Exception("Dynamic can't be lowered")
        if value > 1:
            raise ValueError("Dynamic must be 0 or 1")
        self._dynamic = value

    def _set_optimization_priority(self, value):
        if value < 0 or value > 1:
            raise ValueError("Optimization priority must be 0 or 1")
        self._optimization_priority = value

    dynamic = rwproperty("_dynamic", _set_dynamic)
    optimization_priority = rwproperty("_optimization_priority", _set_optimization_priority)

    action = roproperty("_action")
    class_name = rwproperty("_class_name")
    entries = roproperty("_entries")

    def _finalize(self):
        self._entries._finalize()

        # already dynamic
        if self._dynamic:
            return

        # check action and enable dynamic if exists
        # TODO: check if action has source code
        if self._action:
            log.write("Enable dynamic for %s due to %s action presence" % (self._origin, self._action.name))
            self._dynamic = 1
            return

        # check stateful attribute
        if self._stateful:
            log.write("Enable dynamic for %s due to stateful attribute" % self._origin)
            self._dynamic = 1
            return

        for child in self._entries:
            # object with dynamic child must be dynamic
            if child.dynamic:
                log.write("Enable dynamic for %s due to child dynamic attribute" % self._origin)
                self._dynamic = 1
                return

            # object with handlers must be dynamic too
            if child.on_initialize or child.on_execute or child.on_render or child.on_wysiwyg:
                log.write("Enable dynamic for %s due to handler(s) presence" % self._origin)
                self._dynamic = 1
                return
