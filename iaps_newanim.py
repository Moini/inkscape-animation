#!/usr/bin/python
import sys
import inkex
import simpletransform
import subprocess
import copy
import logging
from simplestyle import *
import animationset.iaps as iaps

class IAPS_NewAnim(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option("--name",action="store",type="string",dest="name",default="newAnim",help="")
		self.OptionParser.add_option("--width",action="store",type="int",dest="width",default="350",help="")
		self.OptionParser.add_option("--height",action="store",type="int",dest="height",default="350",help="")

	def effect(self):
		#retrieve CLI params
		name = self.options.name
		width = self.options.width
		height = self.options.height
		#retrieve document root 
		root = self.document.getroot()
		docw = self.unittouu( root.get("width") )
		doch = self.unittouu( root.get("height") )
		# craft new name and check for duplicates
		anim_id = 'anim_' + name
		anim_id = iaps.get_uid( root, anim_id )
		# retrieve unique name without anim_ prefix
		name = anim_id[ anim_id.find('_') + 1:]
		# start creating things
		anim_layer = iaps.create_layer( root, anim_id )
		rect_layer = iaps.create_layer( anim_layer, 'frame_' + name + '_background')
		iaps.create_rect( rect_layer, width, height, docw, doch, True )
		rect_layer.set(inkex.addNS('insensitive','sodipodi'),'true')

def _main():
	logging.basicConfig( filename='iaps_newanim.log', level = logging.DEBUG )
	e = IAPS_NewAnim()
	e.affect()
	exit()
	
if __name__ == "__main__":
	_main()
