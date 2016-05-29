
from . import lexemes


class vregister(object):

	def __init__(self, names):
		self._names=names

	def get_names(self):
		return self._names

	names=property(get_names)


class vinitialregister(vregister):

	def __init__(self, names=None):
		self._names={} if names is None else names

	def import_names(self, module_name, alias=super):
		if alias is super:
			alias=module_name
		module=__import__("vscript.%s"%module_name).__dict__[module_name]
		for name in dir(module):
			if name.startswith(lexemes.prefix):
				self._names.setdefault(name, alias)

	def get_names(self):
		self.import_names("exceptions", alias=None)
		self.import_names("library", alias=None)
		self.import_names("extensions")
		self.__class__=vregister
		return self._names
		
	names=property(get_names)


register=vinitialregister()
