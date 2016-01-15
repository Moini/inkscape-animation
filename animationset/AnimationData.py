#!/usr/bin/python

class AnimationData( object ):
	def __init__(self, name, rate_ms, region_names, is_forwad = True, is_looped = False,\
			is_pendulum = False ):
		self.name = name
		self.rate_ms = rate_ms
		# create regions
		if region_names is None:
			self.region_names = list()
		else:
			self.region_names = region_names
		# bool flags
		self.is_forward = is_forwad
		self.is_looped = is_looped
		self.is_pendulum = is_pendulum

	def to_json( self ):
		data_string = '\t{\n\t"name":"' + self.name + '",\n'
		data_string = data_string + '\t\t"rate_ms": ' + str(self.rate_ms) + ',\n'
		data_string = data_string + '\t\t"is_forward": ' + str(self.is_forward).lower() + ',\n'
		data_string = data_string + '\t\t"is_looped": ' + str(self.is_looped).lower() + ',\n'
		data_string = data_string + '\t\t"is_pendulum": ' + str(self.is_pendulum).lower() + ',\n' 
		# TODO: regions
		data_string = data_string + '\t\t"regions":[ \n'
		for r in self.region_names:
			data_string = data_string + '\t\t\t"' +  r + '",\n'
		data_string = data_string + '\t\t],\n\t}'

		return data_string
