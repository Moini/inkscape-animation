#!/usr/bin/python
import sys
import inkex
import logging
from simplestyle import *
import animationset.iaps as iaps
from animationset.AnimationExport import AnimationExport

class IAPS_ExportAnim( inkex.Effect ):
	def __init__(self):
		inkex.Effect.__init__(self)
		self.OptionParser.add_option('--useframe',action="store",type="inkbool",dest="use_frame_wh", default="False", help="")
		self.OptionParser.add_option("--framew",action="store",type="int",dest="frame_w",default="320",help="")
		self.OptionParser.add_option("--frameh",action="store",type="int",dest="frame_h",default="320",help="")
		self.OptionParser.add_option("--path",action="store",type="string",dest="path",default=".",help="")
		self.OptionParser.add_option("--gif",action="store",type="inkbool",dest="make_gif",default="True",help="")
		self.OptionParser.add_option("--rate",action="store",type="int",dest="gif_rate",default="50",help="")
		# debug mode 
		self.OptionParser.add_option("--debug",action="store",type="inkbool",dest="debug",default="False",help="")

	def effect(self):
		# retrieve options
		use_frame_wh = self.options.use_frame_wh
		frame_w = self.options.frame_w
		frame_h = self.options.frame_h
		path = self.options.path
		make_gif = self.options.make_gif
		gif_rate = self.options.gif_rate
		# export using AnimationExport class
		a = AnimationExport( self, self.current_layer, path, make_gif, gif_rate, frame_w, frame_h, use_frame_wh, self.options.debug )
		a.export()

def _main():
	logging.basicConfig( filename='iaps_exanim.log', level = logging.DEBUG )
	e = IAPS_ExportAnim()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
