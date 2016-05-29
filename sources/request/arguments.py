
class VDOM_request_arguments:
	"""request arguments"""

	def __init__(self, args):
		""" Constructor """
		self.__arguments = args

	def arguments(self, args=None):
		"""access request property"""
		if args:
			self.__arguments = args
		return self.__arguments
