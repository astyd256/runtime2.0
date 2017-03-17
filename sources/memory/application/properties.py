
from collections import OrderedDict


class MemoryObjectsItemsProperty(object):

    def __get__(self, instance, owner=None):
        with instance._owner.lock:
            instance.__dict__["_items_by_name"] = {}
            return instance.__dict__.setdefault("_items", OrderedDict())


class MemoryObjectsItemsByNameProperty(object):

    def __get__(self, instance, owner=None):
        with instance._owner.lock:
            instance.__dict__["_items"] = OrderedDict()
            return instance.__dict__.setdefault("_items_by_name", {})


memory_objects_items_property = MemoryObjectsItemsProperty
memory_objects_items_by_name_property = MemoryObjectsItemsByNameProperty


class MemoryActionsItemsProperty(object):

    def __get__(self, instance, owner=None):
        with instance._owner.lock:
            instance.__dict__["_items_by_name"] = {}
            return instance.__dict__.setdefault("_items", {})


class MemoryActionsItemsByNameProperty(object):

    def __get__(self, instance, owner=None):
        with instance._owner.lock:
            instance.__dict__["_items"] = {}
            return instance.__dict__.setdefault("_items_by_name", {})


memory_actions_items_property = MemoryActionsItemsProperty
memory_actions_items_by_name_property = MemoryActionsItemsByNameProperty
