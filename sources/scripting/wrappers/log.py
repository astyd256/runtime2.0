
import managers, version, utils


class VDOM_log(object):

	def debug(self, message, *arguments):
		print message%arguments

	def error(self, message, *arguments):
		print message%arguments
