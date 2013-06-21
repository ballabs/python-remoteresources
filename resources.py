import urllib2
import urllib
import re

from deserializers import *


class BaseResource(object):

	def __init__(self):
		raise NotImplementedError('__init__ is not implemented.')

	def __call__(self, **data):
		'''
		Should return the body of the call response already 
		deserialized.
		'''
		raise NotImplementedError('__call__ is not implemented.')

	def _fetch_resource(self, **data):
		raise NotImplementedError('__call__ is not implemented.')

	def _deserialize(self, response_body):
		'''
		Default deserializer will pass the response_body 
		through without performing further operations.
		'''
		return response_body

	def _handle_errors(self, exception, exception_handlers):
		'''
		Iterates through the error handlers
		The first handler that can handle the exception
		is used.
		'''


class HTTPResource(BaseResource):
	base_deserializer = Deserializer
	default_timeout = 300
	
	def __init__(self, method, locator='', deserializers=[], **vars):
		self._setup_vars = {
			'method': method,  # required
			'locator': locator,
			'deserializers': deserializers  # required eventually
		}

		self._setup_vars.update(vars)

	def __call__(self, **data):
		resource = self._fetch_resource(**data)
		return self._deserialize(resource)

	def add_setup_vars(self, **kwargs):
		self._setup_vars.update(kwargs)

	def setup(self):
		setup_vars = self._setup_vars
		self._method = setup_vars['method']
		self._url = setup_vars['url']
		self._deserializers = setup_vars.get('deserializers', [])
		self._locator = setup_vars.get('locator', None)
		self._data = setup_vars.get('data', {})
		self._loggers = setup_vars.get('loggers', [])
		self._timeout = setup_vars.get('timeout', self.default_timeout)
		self._request_logger = setup_vars.get('request_logger', None)
		self._response_logger = setup_vars.get('response_logger', None)

		# VALIDATE HTTP METHOD
		if not validate_method(self._method):
			raise ValueError('Invalid HTTP method! Got "{0}".'.format(self._method))

	def _fetch_resource(self, **data):
		# update data with common data
		data.update(self._data)

		# update locator portion of the url
		if self._locator:
			formated_locator = format_locator(self._locator, data)
		else:
			formated_locator = self._locator

		if self._locator:
			full_url = '{0}{1}'.format(self._url, formated_locator)
		else:
			full_url = self._url

		# remove locator vars/data from data
		data = remove_locator_vars(self._locator, data)

		# encode remaining data
		encoded_vars = urllib.urlencode(data)

		# create request
		if self._method == 'GET':
			# attach data to url
			get_url = '{0}?{1}'.format(
				full_url,
				encoded_vars
			)
			request = urllib2.Request(get_url)
		elif self._method == 'POST':
			request = urllib2.Request(full_url, encoded_vars)
		else:  # other methods
			request = urllib2.Request(full_url, encoded_vars)

		# make call
		try:
			response = urllib2.urlopen(request, timeout=self._timeout)
		except urllib2.HTTPError as e:
			return e.read()
		return response.read()

	def _deserialize(self, response_body):
		'''
		Default deserializer will pass the response_body 
		through without performing further operations.
		'''
		deserializer = self.base_deserializer(response_body)
		deserialized = deserializer.deserialize()
		# run extra deserializers
		for deserializer in self._deserializers:
			deserialized = deserializer(response_body).deserialize()
		return deserialized


class HTTPJSONResource(HTTPResource):
	base_deserializer = JSONDeserializer


class HTTPXMLResource(HTTPResource):
	base_deserializer = XMLDeserializer


class HTTPHTMLResource(HTTPResource):
	pass


class HTTPSOAPResource(HTTPResource):
	base_deserializer = SOAPDeserializer


_valid_methods = [
	'GET',
	'POST',
	'PUT',
	'DELETE'
]


def validate_method(method):
	if method in _valid_methods:
		return True

	return False


def get_locator_var_names(locator):
	'''
	Returns a list of strings representing the 
	variable names in the locator.

	locator:
		string representing all or part of the url.
	'''
	return re.findall('{(\w+)}', locator)


def get_locator_vars(locator, all_vars):
	'''
	Returns a dictionary containing
	corresponding locator variables.

	locator:
		string

	all_vars:
		dictionary
	'''
	locator_var_names = get_locator_var_names(locator)
	if not locator_var_names:
		return None

	locator_vars = {}
	for var_name in locator_var_names:
		locator_vars[var_name] = all_vars[var_name]

	return locator_vars


def remove_locator_vars(locator, all_vars):
	'''
	Returns all_vars with locator vars removed.

	Will raise a KeyError if all_vars does not contain
	var names indicated in locator.

	locator:
		string

	all_vars:
		dictionary
	'''
	locator_var_names = get_locator_var_names(locator)
	for var_name in locator_var_names:
		del(all_vars[var_name])

	return all_vars


def format_locator(locator, all_vars):
	'''
	Returns the formated locator string according
	to the contents of all_vars.

	locator:
		string

	all_vars:
		dictionary
	'''
	locator_vars = get_locator_vars(locator, all_vars)

	if locator_vars:
		return locator.format(**locator_vars)
	else:
		return locator
