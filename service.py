from resources import BaseResource


class Service(object):

	def __init__(self):
		attrs = dir(self)

		# get Meta/Common attributes
		all_meta_attrs = dir(self.Meta)
		meta_attrs = []
		for meta_attr in all_meta_attrs:
			if '__' not in meta_attr:
				meta_attrs.append(meta_attr)
		full_meta_dict =  self.Meta.__dict__
		meta_dict = {}
		for meta_attr in meta_attrs:
			meta_dict[meta_attr] = full_meta_dict[meta_attr]

		# make meta available to all resources.
		for attr_name in attrs:
			attr = getattr(self, attr_name)
			if isinstance(attr, BaseResource):
				for meta_attr in meta_attrs:
					attr.add_setup_vars(**meta_dict)
					attr.setup()


class RESTService(Service):
	pass


class SOAPService(Service):
	pass