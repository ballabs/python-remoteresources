import simplejson as json
from xml.etree import ElementTree


def to_python(data):
    return json.loads(data)


class Deserializer(object):

	def __init__(self, serialized):
		''
		self.serialized = serialized
	
	def deserialize(self):
		return self.serialized


class JSONDeserializer(Deserializer):

	def deserialize(self):
		return to_python(self.serialized)


class XMLDeserializer(Deserializer):

	def deserialize(self):
		return ElementTree.fromstring(self.serialized)


class SOAPDeserializer(Deserializer):
	pass
