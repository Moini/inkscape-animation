#!/usr/bin/python
import sys
import os
import inkex
import logging
from sys import platform as _platform
from simplestyle import *
import animationset.iaps as iaps
from animationset.AnimationExport import AnimationExport
from animationset.SpritesheetMaker import SpritesheetMaker

class IAPS_ExportAnimBatch( inkex.Effect ):
	def __init__(self):
		inkex.Effect.__init__(self)
		# custom framesize options
		self.OptionParser.add_option('--useframe',action="store",type="inkbool",dest="use_frame_wh", default="False", help="")
		self.OptionParser.add_option("--framew",action="store",type="int",dest="frame_w",default="320",help="")
		self.OptionParser.add_option("--frameh",action="store",type="int",dest="frame_h",default="320",help="")
		# path options
		self.OptionParser.add_option("--path",action="store",type="string",dest="path",default=".",help="")
		self.OptionParser.add_option("--folder",action="store",type="inkbool",dest="create_folder",default="True",help="")
		self.OptionParser.add_option("--res",action="store",type="inkbool",dest="append_resolution",default="True",help="")
		# gif creation options
		self.OptionParser.add_option("--gif",action="store",type="inkbool",dest="make_gif",default="True",help="")
		self.OptionParser.add_option("--rate",action="store",type="int",dest="gif_rate",default="50",help="")
		# spritesheet options
		self.OptionParser.add_option("--spritename",action="store",type="string",dest="sprite_name",default="Sprite",help="")
		self.OptionParser.add_option("--sprite",action="store",type="inkbool",dest="make_sprite",default="True",help="")
		self.OptionParser.add_option("--texturew",action="store",type="int",dest="texture_w",default="1024",help="")
		self.OptionParser.add_option("--textureh",action="store",type="int",dest="texture_h",default="1024",help="")
		# debug mode 
		self.OptionParser.add_option("--debug",action="store",type="inkbool",dest="debug",default="False",help="")

	def effect(self):
		# retrieve CLI options
		use_frame_wh = self.options.use_frame_wh
		frame_w = self.options.frame_w
		frame_h = self.options.frame_h
		path = self.options.path
		create_folder = self.options.create_folder
		append_resolution = self.options.append_resolution
		make_gif = self.options.make_gif
		gif_rate = self.options.gif_rate
		#retrieve sprite creation options
		make_sprite = self.options.make_sprite
		sprite_name = self.options.sprite_name
		texture_w = self.options.texture_w
		texture_h = self.options.texture_h

		# get document root
		root = self.document.getroot()
		# get current SVG filename
		svg_file =self.args[-1]
		# go through nodes
		nodes = root.getchildren()
		actual_path = path
		animationData = list()
		regionPaths = list()
		for n in nodes:
			node_id = n.get('id')
			if -1 != node_id.find('anim_'):
				clean_id = node_id[node_id.find('_')+1:]
				if create_folder:
					#create folder name
					if "win32" == _platform:
						actual_path = path + '\\' + clean_id
					else:
						actual_path = path + '/' + clean_id
					#process resolution name part
					if append_resolution and use_frame_wh:
						if "win32" == _platform:
							actual_path = path + '\\' + clean_id + '_' + str(frame_w) + 'x' + str(frame_h)
						else:
							actual_path = path + '/' + clean_id + '_' + str(frame_w) + 'x' + str(frame_h)
					if not os.path.isdir( actual_path ):
						os.makedirs( actual_path )
				a = AnimationExport( self, n, actual_path, make_gif, gif_rate, frame_w, frame_h, use_frame_wh, self.options.debug )
				animData = a.export()
				animationData.append( animData.json_data )
				regionPaths.append( animData.region_paths )
		# TODO: if export json: create regions, invoke imagemagick
		if False == make_sprite:
			return
		texture_name = sprite_name + '.png'
		if "win32" == _platform:
			fq_sprite_path = path + '\\' + texture_name 
			fq_json_path = path + '\\' + sprite_name + '.json'
		else:
			fq_sprite_path = path + '/' + texture_name 
			fq_json_path = path + '/' + sprite_name + '.json'
		if self.options.debug:
			logging.debug( 'Using sprite sheet path: ' + fq_sprite_path + '\n' )
			logging.debug( 'Using json markup path: ' + fq_json_path + '\n' )
		s_maker = SpritesheetMaker( fq_sprite_path, regionPaths, frame_w, frame_h, texture_w, texture_h, self.options.debug )
		s_maker.make_spritesheet()
		regions_markup = s_maker.make_markup()
		# create json data
		json_data = '{\n'
		json_data = json_data + '\t"set_name":"' + sprite_name + '",\n'
		json_data = json_data + '\t"texture":"' + texture_name + '",\n'
		json_data = json_data + '\t"regions":[\n'
		json_data = json_data + regions_markup + ' \t],\n'
		json_data = json_data + '\t"animations":[\n'
		for a in animationData:
			json_data = json_data + a + ',\n'
		json_data = json_data + '\t],\n'
		json_data = json_data + '}'
		# debug output
		if self.options.debug:
			logging.debug( "JSON data:\n")
			logging.debug( json_data + '\n\n' )
		# write out json file
		json_file = open( fq_json_path, 'w' )
		json_file.write( json_data );
		json_file.close()

def _main():
	logging.basicConfig( filename='iaps_exanimbatch.log', level = logging.DEBUG )
	e = IAPS_ExportAnimBatch()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
