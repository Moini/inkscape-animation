#!/usr/bin/python

class RegionData(object):
	def __init__(self, name, x = 0, y = 0, w = 32, h = 32):
		self.name = name
		self.x = x
		self.y = y
		self.w = w
		self.h = h
		pass
	def to_json(self):
		data_string = '{ "name":"'+self.name+'", "x":'+str(self.x)+', "y":' +  str(self.y) + ', '
		data_string = data_string + '"w":' + str(self.w) + ', "h":'+str(self.h) + ' }'
		return data_string
