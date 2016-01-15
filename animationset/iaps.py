import sys
import copy
import os
import inkex
import subprocess
import logging

# create new bw rectangle ( w*h ) in specified layer, centered to document, if needed;
def create_rect( layer, w, h, docw, doch, center ):
	rect = inkex.etree.SubElement( layer, 'rect' )
	rect.set('id', 'rect_' + layer.get( 'id' ) )
	rect.set('width', str(w) )
	rect.set('height', str(h) )
	rect.set('rx', '0' )
	rect.set('ry', '0' )
	x = 0
	y = 0
	if center:
		x = docw / 2 - w / 2;
		y = doch / 2 - h / 2;

	rect.set('x', str( x ) )
	rect.set('y', str( y ) )
	rect.set('style', "color:#000000;display:inline;overflow:visible;visibility:visible;opacity:1;fill:#ffffff;fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:5;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;marker:none;enable-background:accumulate")
	return rect

# create w*h rectangle with top-left corner at x,y
def create_rect_xy( layer, x, y, w, h, center = False, docw = 0, doch = 0 ):
	rect = inkex.etree.SubElement( layer, 'rect' )
	rect.set('id', 'rect_' + layer.get( 'id' ) )
	rect.set('width', str(w) )
	rect.set('height', str(h) )
	rect.set('rx', '0' )
	rect.set('ry', '0' )
	curx = x
	cury = y
	if center:
		curx = docw / 2 - w / 2
		cury = doch / 2 - h / 2
	rect.set('x', str( curx ) )
	rect.set('y', str( cury ) )
	rect.set('style', "color:#000000;display:inline;overflow:visible;visibility:visible;opacity:1;fill:#ffffff;fill-opacity:1;fill-rule:evenodd;stroke:#000000;stroke-width:5;stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1;marker:none;enable-background:accumulate")
	return rect

# create new (sub) layer
def create_layer( root, layername ):
	layer = inkex.etree.SubElement( root, 'g')
	layer.set(inkex.addNS('label','inkscape'), layername )
	layer.set(inkex.addNS('groupmode','inkscape'), 'layer' )
	layer.set('id', layername )
	return layer

def copy_layer( root, src_layer, layername ):
	xml = inkex.etree.tostring( src_layer )
	new_layer = inkex.etree.fromstring( xml )
	new_layer.set(inkex.addNS('label','inkscape'), layername )
	new_layer.set(inkex.addNS('groupmode','inkscape'), 'layer' )
	new_layer.set('id', layername )
	root.append( new_layer )
	# make copied layer unchangeable
	src_layer.set(inkex.addNS('insensitive','sodipodi'),'true')
	return new_layer

# group selected items in the picked layer
def group_selection( layer, selection ):
	# create group
	g = inkex.etree.SubElement( layer, 'g')
	g.set('id','tempgroup')
	# get children in order
	# move all selected things to the group
	for id, node in reversed( list( selection.iteritems() ) ):
		g.append( node )
	# finish
	return g

# move group contents to the picked layer and remove group
def ungroup_selection( group ):
	# get parent
	parent = group.getparent()
	# move all contents to the layer
	for node in group.getchildren():
		group.remove( node )
		parent.append( node )
	#remove group
	parent = group.getparent()
	parent.remove( group )

# find unique id for a node
def get_uid( root, uid ):
	nodes = root.getchildren()
	for n in nodes:
		node_id = n.get('id')
		if uid == node_id:
			uid = get_uid( root, uid + '0' )
	return uid


# create new frame layer in named anim layer group
def create_frame_layer( current_layer ):
	anim_layer = None
	layertag = current_layer.get('id')
	logging.debug( 'Current layer tag: ' + layertag + '\n')
	duplicate = False
	# if frame layer selected - get its root
	if -1 != layertag.find('frame_'):
		logging.debug('frame_ indicator found\n')
		anim_layer = current_layer.getparent()
		# duplicate active frame if it's not background 
		if -1 == layertag.find('_background'):
			duplicate = True
			logging.debug('will duplicate current layer\n')
	# check if this is animation layer
	if None == anim_layer and -1 != layertag.find( 'anim_' ):
		logging.debug('anim_ found\n')
		anim_layer = current_layer
	# exit, if no animation layer group found
	if None == anim_layer:
		logging.debug('anim_ layer group must be active for this plugin to work.\n')
		return
	# get animation layer group name
	animname_full = anim_layer.get('id')
	tmp1 = animname_full.find('_')
	animname = animname_full[tmp1 + 1:]
	# count animation frames
	frame_layers = anim_layer.getchildren()
	frame_indexes = list()
	for l in frame_layers:
		lname = l.get('id')
		if -1 == lname.find('frame_' + animname + '_background' ) and -1 != lname.find('frame_'):
			tmp1 = lname.find('_')
			tmp2 = lname.find('_', tmp1 + 1 )
			index = lname[tmp2 + 1:]
			logging.debug('Taking frame layer index ' + index + ' in account\n')
			frame_indexes.append( int(index) )
	# calculate next frame numerical index
	max_index = 0
	if len( frame_indexes ) > 0:
		max_index = max(frame_indexes) 
	framename = 'frame_' + animname + '_' + str( max_index + 1 )
	logging.debug('Creating new frame for animation `' + animname + '`:' + framename + '\n')
	l = None
	if duplicate:
		l = copy_layer( anim_layer, current_layer, framename )
		# if prev layer isn't a background - make it less opaque
		current_layer.set('style','opacity:0.25')
	else:
		l = create_layer( anim_layer, framename )
	return l


# export single animation
def export_single_anim( effect, current_layer, svg_file, use_frame_wh, frame_w, frame_h, path, make_gif, gif_rate ):
	logging.debug('File: ' + svg_file + '\n')
	# detect top animation layer
	layer_id = current_layer.get('id')
	top_layer = None
	if -1 != layer_id.find('anim_'):
		top_layer = current_layer
	if -1 != layer_id.find('frame_'):
		top_layer = current_layer.getparent()
	# simple error check
	if None == top_layer:
		logging.debug('Cant export animation from non-animation layer.')
		exit()
	# get clean animation name
	top_layer_id = top_layer.get('id')
	clean_id = top_layer_id[ top_layer_id.find('_')+1:]
	logging.debug('clean animation name: ' + clean_id + '\n')
	# craft bg layer id
	bg_layer_id = 'frame_' + clean_id + '_background'
	logging.debug('bg layer name: ' + bg_layer_id + '\n')
	# retrieve frames list
	bg_layer = None
	frames = list()
	for l in top_layer.getchildren():
		layer_id = l.get('id')
		# detect animation frames
		if -1 != layer_id.find('frame_') and layer_id != bg_layer_id:
			frames.append(l)
		# detect background frame layer
		if bg_layer_id == layer_id:
			bg_layer = l
	# get background rectangle
	rect = None
	rect_id = 'rect_' + bg_layer_id
	logging.debug('bg rect name: ' + rect_id + '\n')
	for n in bg_layer.getchildren():
		n_id = n.get('id')
		if rect_id == n_id:
			rect = n
	# get rectangle dimensions
	x = effect.unittouu( rect.get('x') )
	y = effect.unittouu( rect.get('y') )
	w = effect.unittouu( rect.get('width') )
	h = effect.unittouu( rect.get('height') )
	# calculate zone extends
	#x1 = x + w
	#y1 = y + h
	# document dimensions
	actual_w = effect.uutounit( w, 'mm' )
	actual_h = effect.uutounit( h, 'mm' )
	# traverse through these, exporting their images
	#zone= str(x) + ':' + str(y) + ':' + str(x1) + ':' + str(y1)
	logging.debug('calculated zone: ' + zone + '\n')
	# detect 'defs' section of current XML file
	defs = None
	for child in effect.document.getroot().getchildren():
		tag = child.tag[child.tag.find("}")+1:]
		# remember defines: gradients and etc.
		if tag == "defs":
			defs = child
			logging.debug("Found 'defs' section.\n")
	# prepare directory for svg files
	svg_dir = path + '/svg'
	if not os.path.isdir( svg_dir ):
		os.makedirs( svg_dir )
	# keep track of all created svg files
	svg_filenames = list()
	# export desired layers to series of SVGs
	for f in frames:
		# set frame visible and opaque
		f.set('style','opacity:1.0;display:inline')
		# craft filename and export command
		short_name = f.get('id') + '.svg'
		filename = svg_dir + '/' + short_name
		svg_filenames.append( filename )
		logging.debug('Will export SVG to ' + filename + '\n')
		new_svg = open( filename, 'w' )
		new_svg.write('<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n')
		new_svg.write('<svg\n')
		new_svg.write('width="' + str(actual_w) + 'mm"\n')
		new_svg.write('height="' + str(actual_h) + 'mm"\n')
		new_svg.write('viewBox="' + str(x) + ' ' + str(y) + ' ' + str(w) + ' ' + str(h) + '"\n')
		new_svg.write('sodipodi:docname="' + short_name + '">\n')
		if None != defs:
			new_svg.write( inkex.etree.tostring( defs ) + '\n' )
		new_svg.write( inkex.etree.tostring( f ) + '\n' + '</svg>\n')
		new_svg.close()
	# keep track of pngs for further GIF creation ( if needed )
	png_filenames = list()
	# prepare dir for png
	png_dir = path + '/png'
	if not os.path.isdir( png_dir ):
		os.makedirs( png_dir )
	# write png files
	for filename in svg_filenames:
		short_name = filename[ filename.rfind('/')+1: filename.rfind('.')]
		logging.debug('Png file shortname: ' + short_name + '\n' )
		png_filename = png_dir + '/' + short_name + '.png'
		png_filenames.append( png_filename )
		logging.debug('Will export SVG to ' + png_filename + '\n')
		cmd = None
		if ( use_frame_wh ):
			cmd = ('inkscape','-z','-e',png_filename,'-w',str(frame_w), '-h', str(frame_h), filename)
		else:
			cmd = ('inkscape','-z','-e',png_filename,'-w',str(w), '-h', str(h), filename)
		logging.debug('Export call: ' + str(cmd) + '\n')
		p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		msg = p.communicate()
		logging.debug( msg[ 0 ] + '\n' + msg[1] + '\n' )
	if make_gif:
		# prepare GIF directory
		gif_dir = path + '/gif'
		if not os.path.isdir( gif_dir ):
			os.makedirs( gif_dir )
		# start creating GIF
		logging.debug('Creating animated GIF...\n')
		all_png = png_dir + '/*.png'
		gif_file = gif_dir + '/' + clean_id + '.gif'
		cmd = ('convert','-delay',str(gif_rate),'-dispose','2', all_png, gif_file )
		logging.debug('GIF creation call: ' + str(cmd) + '\n')
		p = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
		msg = p.communicate()
		logging.debug( msg[ 0 ] + '\n' + msg[1] + '\n' )
