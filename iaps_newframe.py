#!/usr/bin/python
import sys
import inkex
import logging
from simplestyle import *
import animationset.iaps as iaps

class IAPS_NewFrame(inkex.Effect):
	def __init__(self):
		inkex.Effect.__init__(self)
	
	def effect(self):
		iaps.create_frame_layer( self.current_layer )


def _main():
	logging.basicConfig( filename='iaps_newframe.log', level = logging.DEBUG )
	e = IAPS_NewFrame()
	e.affect()
	exit()

if __name__=="__main__":
	_main()
