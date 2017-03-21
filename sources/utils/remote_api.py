import re, md5
import threading
import socket

import SOAPpy
from utils.exception import VDOMServiceCallError

from scripting.soap.soaputils import VDOM_session_protector


__version__ = '0.1.4'


session_id_re = re.compile("\<SessionId\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionId\>")
session_key_re = re.compile("\<SessionKey\>\<\!\[CDATA\[(\S+)\]\]\>\<\/SessionKey\>")
hash_string_re = re.compile("\<HashString\>\<\!\[CDATA\[(\S+)\]\]\>\<\/HashString\>")
key_re = re.compile("\<Key\>(\S+)_\d+\<\/Key\>")



class VDOMServiceSingleThread(object):
	def __init__(self, url, login, md5hexpass, application_id):
		self._url = url
		self._login = login
		self._md5hexpass = md5hexpass
		self._application_id = application_id

		self._request_num = 0
		self._skey = None
		self._sid = None
		self._skey = None

		self._server = self.__create_soap_proxy(url)
		self._protector = None


	def __try_connect(self, url, exception=False):
		try:
			# need to update socket.defaulttimeout because SOAPpy is ignoring "timeout" "parameter for HTTPS connections
			socket_timeout = socket.getdefaulttimeout()
			socket.setdefaulttimeout(1)

			service = SOAPpy.SOAPProxy(url.rstrip('/') + '/SOAP', namespace='http://services.vdom.net/VDOMServices')
			service.keep_alive('', '')

			self._url = url
			return service

		except:
			if exception: raise

		finally:
			socket.setdefaulttimeout(socket_timeout)

		return None


	def __create_soap_proxy(self, url):
		def define_best_ssl_context(url, exception=False):
			service = self.__try_connect(url)
			if service is not None: return service

			try:
				import ssl
				ssl._create_default_https_context = ssl._create_unverified_context
				return self.__try_connect(url, exception=True)

			except:
				if exception: raise

			return None

		if url.lower().startswith('https://'):
			return define_best_ssl_context(url, exception=True)

		if '://' in url:
			return self.__try_connect(url, exception=True)

		service = define_best_ssl_context('https://' + url)
		if service is not None: return service

		return self.__try_connect('http://' + url, exception=True)


	def __request_skey(self):
		return '{0}_{1:d}'.format(self._skey, self._request_num)


	def open_session(self):
		login_result = self._server.open_session(self._login, self._md5hexpass)

		self._request_num = 0

		self._sid = str(session_id_re.search(login_result, 1).group(1))
		skey = str(session_key_re.search(login_result, 1).group(1))
		hash_string = str(hash_string_re.search(login_result, 1).group(1))

		self._protector = VDOM_session_protector(hash_string)
		self._skey = self._protector.next_session_key(skey)

		return self


	def call(self, container_id, action_name, xml_data):
		xml_param = "<Arguments><CallType>server_action</CallType></Arguments>"
		ret = None

		try:
			ret = self._server.remote_call(self._sid, self.__request_skey(), self._application_id, container_id, action_name, xml_param, xml_data)

		except Exception, ex:
			if ret:
				raise VDOMServiceCallError( str(ret) )
			else:
				raise VDOMServiceCallError( ex.message  )

		self._skey = self._protector.next_session_key(self._skey)
		self._request_num += 1

		return key_re.sub('', ret)


	def remote(self, method_name, params=None, no_app_id=False):
		params = params or []

		if not no_app_id:
			params.insert(0, self._application_id)

		ret = None
		try:
			soap_method = getattr(self._server, method_name)
			ret = soap_method(self._sid, self.__request_skey(), *params)

		except Exception, ex:
			if ret:
				raise VDOMServiceCallError( str(ret) )
			else:
				raise VDOMServiceCallError( ex.message  )

		self._skey = self._protector.next_session_key(self._skey)
		self._request_num+=1

		return key_re.sub('', ret)


	@classmethod
	def connect(cls, url, login, md5_hexpass, application_id):
		service = cls(url, login, md5_hexpass, application_id)
		return service.open_session()







class VDOMServiceMultiThread(VDOMServiceSingleThread):
	def __init__(self, url, login, md5hexpass, application_id):
		VDOMServiceSingleThread.__init__(self, url, login, md5hexpass, application_id)
		self.__thread = threading.local()


	def api(self):
		if getattr(self.__thread, 'api', None) is None:
			self.__thread.api = VDOMServiceSingleThread(self._url, self._login, self._md5hexpass, self._application_id)
			self.__thread.api.open_session()
		return self.__thread.api


	def open_session( self ):
		self.api().open_session()
		return self


	def call( self, container_id, action_name, xml_data ):
		return self.api().call(container_id, action_name, xml_data)


	def remote(self, method_name, params=None, no_app_id=False):
		return self.api().remote(method_name, params, no_app_id)




VDOMService = VDOMServiceMultiThread
VDOM_service = VDOMServiceMultiThread