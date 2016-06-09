
from .. import errors
from ..subtypes import generic, integer, v_mismatch
from ..variables import variant


class v_list(generic):

	def __init__(self):
		generic.__init__(self)
		self._items=[]


	items=property(lambda self: self._items)


	def erase(self, *arguments):
		if arguments:
			if len(arguments)>1: raise errors.wrong_number_of_arguments
			try: del self._items[argument[0].as_integer]
			except KeyError: raise errors.subscript_out_of_range
		else:
			self._value.clear()
	

	def v_count(self, **keywords):
		if "let" in keywords or "set" in keywords:
			raise errors.errors.object_has_no_property
		else:
			return integer(len(self._items))
	

	def v_append(self, value):
		self._items.append(value.subtype)
		return v_mismatch

	def v_insert(self, index, value):
		self._items.insert(as_integer(index), value.subtype)
		return v_mismatch

	def v_remove(self, value):
		try: self._items.remove(value.subtype)
		except ValueError: raise errors.element_not_found
		return v_mismatch

	def v_index(self, value):
		try: return self._items.index(value.subtype)
		except ValueError: raise errors.element_not_found

	def v_push(self, value):
		self._items.append(value.subtype)
		return v_mismatch

	def v_pop(self, index=None):
		try: return self._items.pop(-1 if index is None else index.as_integer)
		except KeyError: raise errors.subscript_out_of_range
	
	
	def __iter__(self):
		for item in self._items: yield variant(item)
	
	def __len__(self):
		return integer(len(self._items))
