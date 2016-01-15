#!/usr/bin/python

import inkex
import os
import subprocess
import sys
import logging
from sys import platform as _platform
from AnimationData import AnimationData

class FrameLayer( object ):
	def __init__( self, name, layer ):
		self.name = name
		self.layer = layer

class AnimationExportData( object ):
	def __init__( self, json_data, region_paths ):
		self.json_data = json_data
		self.region_paths = region_paths


class AnimationExport(object):

	def __init__(self, effect, layer, path, make_gif = True, gif_rate=100, arg_w = 320, arg_h = 320, use_arg_dimensions = False, debug = False ):
		self.effect = effect
		self.path = path
		self.make_gif = make_gif
		self.gif_rate = gif_rate
		self.debug = debug
		if "win32" == _platform:
			self.svg_path = path + '\\svg'
			self.png_path = path + '\\png'
			self.gif_path = path + '\\gif'
		else:
			self.svg_path = path + '/svg'
			self.png_path = path + '/png'
			self.gif_path = path + '/gif'
		self.create_dirs()
		self.top_layer = self.get_animation_top_layer( layer )
		self.name = self.get_animation_name()
		self.bg_name = 'frame_' + self.name + '_background'
		self.bg_rect_name = 'rect_' + self.bg_name
		self.bg_layer = self.get_bg_layer()
		self.bg_rect = self.get_bg_rect()
		self.geom = self.get_bg_rect_geometry()
		self.arg_w = arg_w
		self.arg_h = arg_h
		self.use_arg_dimensions = use_arg_dimensions
		self.frames = self.get_animation_frames()
		self.defs = self.get_svg_defs()

	def create_dirs(self):
		if self.debug:
			logging.debug("Creating export directories.\n")
		dirs = [ self.png_path, self.svg_path, self.gif_path ]
		for path in dirs:
			if not os.path.isdir( path ):
				os.makedirs( path )
				if self.debug:
					logging.debug("Created '" + path + "'")

	def get_animation_top_layer( self, layer ):
		current_id = layer.get('id')
		top_layer = None
		if -1 != current_id.find('anim_'):
			top_layer = layer
		if -1 != current_id.find('frame_'):
			top_layer = layer.getparent()
		###assert top_layer is None
		return top_layer

	def get_animation_name( self ):
		#assert self.top_layer is None
		raw_name = self.top_layer.get('id')
		clean_name = raw_name[ raw_name.find('_')+1:]
		return clean_name

	def get_bg_layer( self ):
		#assert self.top_layer is None
		for node in self.top_layer.getchildren():
			name = node.get('id')
			if name == self.bg_name:
				return node
		return None

	def get_bg_rect( self ):
		#assert self.bg_layer is None
		for node in self.bg_layer.getchildren():
			name = node.get('id')
			if name == self.bg_rect_name:
				return node
		return None

	def get_animation_frames( self ):
		#assert self.top_layer is None
		frames = list()
		for node in self.top_layer.getchildren():
			name = node.get('id')
			if -1 != name.find('frame_') and name != self.bg_name:
				f = FrameLayer ( name, node )
				frames.append( f )
		return frames

	def get_svg_defs( self ):
		root = self.effect.document.getroot()
		for node in root.getchildren():
			name = node.tag[ node.tag.find("}") + 1:]
			if "defs" == name:
				return node
		return None

	def get_bg_rect_geometry( self ):
		#assert self.bg_rect is None
		x = self.effect.unittouu( self.bg_rect.get('x') )
		y = self.effect.unittouu( self.bg_rect.get('y') )
		w = self.effect.unittouu( self.bg_rect.get('width') )
		h = self.effect.unittouu( self.bg_rect.get('height') )
		# dimensions for future document, in units
		uw = self.effect.uutounit( w, 'mm' )
		uh = self.effect.uutounit( h, 'mm' )
		# resulting dictionary
		data = { 'x':x, 'y':y, 'w':w, 'h':h, 'uw':uw, 'uh':uh }
		return data

	def export( self ):
		#assert self.frames is None
		#assert self.geom is None
		svg_filenames = list()
		png_filenames = list()
		# get dimensions
		x = self.geom['x']
		y = self.geom['y']
		w = self.geom['w']
		h = self.geom['h']
		uw = self.geom['uw']
		uh = self.geom['uh']
		exRegionNames = list()
		exRegionPaths = list()
		# go through all frames
		for frame in self.frames:
			# export to svg
			name = frame.name
			exRegionNames.append( name )
			layer = frame.layer
			layer.set('style','opacity:1.0;display:inline')
			if "win32" == _platform:
				outfile_svg = self.svg_path + '\\' + name + '.svg'
			else:
				outfile_svg = self.svg_path + '/' + name + '.svg'
			svg_filenames.append( outfile_svg )
			# write to file
			new_svg = open( outfile_svg, 'w' )
			new_svg.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
			new_svg.write('<svg\n')
			new_svg.write('width="' + str(uw) + 'mm"\n')
			new_svg.write('height="' + str(uh) + 'mm"\n')
			new_svg.write('viewBox="' + str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '"\n')
			new_svg.write('sodipodi:docname="' + name + '.svg">\n')
			if None != self.defs:
				new_svg.write( inkex.etree.tostring( self.defs ) + '\n' )
			new_svg.write( inkex.etree.tostring( layer ) + '\n' + '</svg>\n')
			new_svg.close()
			# make exported layer invisible
			layer.set('style','opacity:1.0;display:none')
			# export to png
			if "win32" == _platform:
				outfile_png = self.png_path + '\\' + name + '.png'
			else:
				outfile_png = self.png_path + '/' + name + '.png'
			exRegionPaths.append( outfile_png )
			cmd = None
			if self.use_arg_dimensions:
				cmd = ('inkscape', '-z', '-e', outfile_png, '-w', str(self.arg_w), '-h', str(self.arg_h), outfile_svg )
			else:
				cmd = ('inkscape', '-z', '-e', outfile_png, '-w', str(w), '-h', str(h), outfile_svg )
			#assert cmd is None
			p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
			msg = p.communicate()
			if self.debug:
				logging.debug( str(cmd) + "\n" )
		# make first frame layer visible
		first_layer = self.frames[0].layer
		first_layer.set('style','opacity:1.0;display:inline')
		# prepare json data
		exportData = AnimationData( self.name, 150, exRegionNames )

		# generate GIF file, using imagemagick
		if self.make_gif is True:
			# create output file path
			if "win32" == _platform:
				outfile_gif = self.gif_path + "\\" + self.name + '.gif'
			else: # assume Linux or MacOS
				outfile_gif = self.gif_path + '/' + self.name + '.gif'

			# obtain common info
			numframes = len(self.frames)
			files_regex = 'frame_' + self.name + '_[1-' + str(numframes) + '].png'

			# create regular expression for all the png files
			if "win32" == _platform:
				png_regex = self.png_path + '\\' + files_regex
			else:
				png_regex = self.png_path + '/' + files_regex
			# calc rate in a form appropriate for 'convert' tool
			r = self.gif_rate / 10
			# GIF creation command
			cmd = ('convert','-delay',str(r),'-dispose','2', png_regex, outfile_gif )
			if "win32" == _platform:
				p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True )
			else:
				p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			msg = p.communicate()
			if self.debug:
				logging.debug( "GIF command: '" + str(cmd) + "'.\n")
				if "win32" == _platform:
					logging.debug( msg[0].decode('cp866') + "\n" )
					logging.debug( msg[1].decode('cp866') + "\n" )
				else:
					logging.debug( msg[0] + "\n" )
					logging.debug( msg[1] + "\n" )


		if self.debug:
			logging.debug("JSON data:\n")
			logging.debug( exportData.to_json() + '\n\n' )
			logging.debug("Export region paths:\n")
			for p in exRegionPaths:
				logging.debug( p + "\n" )
		resultData = AnimationExportData( exportData.to_json(), exRegionPaths )
		return resultData
