import subprocess
import os
import sys
import logging
from sys import platform as _platform
from RegionData import RegionData

class SpritesheetMaker( object ):

	""" generate spritesheet from specified region paths, using single sprite size w*h, 
		creating texture tex_w*tex*h
	"""
	#def __init__(self, fq_filepath, region_paths, w, h, tex_w, tex_h, debug = False ):
	def __init__(self, fq_filepath, region_paths, w, h, frames_x, frames_y, debug = False ):
		self.path = fq_filepath
		self.region_paths = region_paths
		self.w = w
		self.h = h
		#self.texture_w = tex_w
		#self.texture_h = tex_h
		self.frames_x = frames_x
		self.frames_y = frames_y
		self.debug = debug
		num = 0
		for s in region_paths:
			num = num + len ( s )
		# overall number of frames
		self.size = num
		# columns num
		#self.n = self.texture_w // self.w 
		# rows num
		#self.m = self.size // self.n + 1
		# output info
		if self.debug:
			logging.debug('Obtained ' + str( self.size ) + ' frames \n' )
			logging.debug( 'Will use ' + str( self.frames_x ) + 'x' + str( self.frames_y ) + ' tileset\n' )

	# compose spritesheet image from given files
	def make_spritesheet( self ):
		cmd = ( 'montage', ) 
		for r in self.region_paths:
			for p in r:
				cmd = cmd + (p, )
		#cmd = cmd + ('-tile', str( self.n ) + 'x' + str( self.m + 1 ), '-geometry',\
		#		str(self.w) +'x'+str(self.h) +':0:0','-background', 'transparent', self.path )
		cmd = cmd + ('-tile', str( self.frames_x ) + 'x' + str( self.frames_y + 1 ), '-geometry',\
				str(self.w) +'x'+str(self.h) +':0:0','-background', 'transparent', self.path )
		if self.debug:
			logging.debug( "Sprite assembly cmd:" + str( cmd ) + '\n' )
		proc = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		res = proc.communicate()
		if self.debug:
			logging.debug( res[0] + '\n' )
			logging.debug( res[1] + '\n' )

	# creates a json markup for all the regions
	def make_markup( self ):
		# regions counter
		i = 0
		# regions json
		json_data = ''
		# each region_paths entry is a list
		for path_set in self.region_paths:
			#go through actual list
			for p in path_set:
				if "win32" == _platform:
					name = p[ p.rfind('\\') + 1: ]
				else:
					name = p[ p.rfind('/') + 1: ]
				name = name[ :name.rfind('.png') ]
				#y = ( i // self.n ) 
				#x = ( i - y * self.n ) * self.w
				y = ( i // self.frames_x ) 
				x = ( i - y * self.frames_x ) * self.w
				y = y * self.h
				r_data = RegionData( name, x, y, self.w, self.h )
				json = '\t\t' + r_data.to_json() + ',\n'
				if self.debug:
					logging.debug( "JSON data:\n" )
					logging.debug( json + "\n" )
				json_data = json_data + json
				i = i + 1
		return json_data
