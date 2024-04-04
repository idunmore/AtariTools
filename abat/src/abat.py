#!python3

# Native Python Modules
from enum import Enum
from pathlib import Path
from urllib.request import urlretrieve

# External Modules
import click
from PIL import Image

# "The Cover Project" - Constants
CDN_BASE = "https://coverproject.sfo2.cdn.digitaloceanspaces.com/"
SYSTEM_BASE = "atari_"
SOURCE_PREFIX ="tcp_"
SOURCE_FILE_EXT = ".jpg"
SYSTEM_PREFIXES = ["a", ""]

# The SPACE character is significant here, so do not remove.
INVALID_NAME_CHARS = " _.-'!?"

# Alternates COVERS are numbered from 2 (the first file is the main file and is
# presumed to be number 1, even though it has no numer suffix).
FIRST_ALTERNATE = 2
MAX_ALTERNATES = 5

# "Atari Gamestation Pro" - Constants
CROP_WIDTH = 236
CROP_HEIGHT = 322
ASPECT_RATIO = CROP_WIDTH / CROP_HEIGHT

COVER_WIDTH = 236
COVER_HEIGHT = 332

COVER_EXT = ".png"

# AGSPTOOL Constants
FRONT_OPTION = "front"
BACK_OPTION = "back"

# Image Size Tuple Indexes
WIDTH = 0
HEIGHT = 1

@click.group()
def abat():
	'''"Atari Gamestation Pro" (AGP) Box Art Tool (ABAT).

		Creates box covers for the Atari Gamestation Pro "Atari "Games"
		interface, with a single command.

		Separate utility functions to fetch high-quality box art for a given
		Atari system and game, crop out front or back covers from a raw box art
		file, and resize covers to the native size for main AGP interface.
	'''
	pass

@abat.command("cover")
@click.option('-s', '--system',
	type=click.Choice(['2600', '5200', '7800']),
	default='2600', show_default=True, help='Atari system')
@click.option('-d', '--delete', is_flag=True, default=False,
	help="Delete original box art file")
@click.argument('game')
@click.argument('dest_path',
	type=click.Path(exists=True, file_okay=False, dir_okay=True), default='./')
@click.argument('filename',
	type=click.Path(exists=False, file_okay=True, dir_okay=False), default='')
def cover(system, delete, game, dest_path, filename):
	'''Fetches, extracts and sizes box cover files for the AGSP.'''
	try:		
		# Fetch the basic cover file.
		box_art_name, box_art_extension = build_dest_filename_and_ext(
			dest_path, SOURCE_PREFIX, system, None, game )
		box_art_filename = f'{box_art_name}{box_art_extension}'
		result = fetch_box_art(system, game, dest_path, box_art_filename, False)

		# Crop out the bit we need.
		cover = create_cropped_image(FRONT_OPTION, box_art_filename, ASPECT_RATIO)

		# Resize the cropped image.
		top, resize_height = get_padding_and_height(True)
		resized_image = create_resized_image(cover, top, resize_height)

		# If no filename was specifeid, use the game name.
		if filename is None or len(filename) == 0:
			filename=f'{game}{COVER_EXT}'

		dest_filename = Path(dest_path) / Path(filename)		
		resized_image.save(dest_filename, "PNG", optimize=True)

		# Delete the original box art file if requested
		if delete:
			box_art_file = Path(dest_path) / Path(box_art_filename)
			Path.unlink(box_art_file)

		exit(0)

	except Exception as e:
		exit(1)


@abat.command("fetch")
@click.option('-s', '--system',
	type=click.Choice(['2600', '5200', '7800']),
	default='2600', show_default=True, help='Atari system')
@click.option('-a', '--alternates', is_flag=True, default=False,
	help='Attempt to fetch alternate covers')
@click.argument('game')
@click.argument('dest_path',
	type=click.Path(exists=True, file_okay=False, dir_okay=True), default='./')
@click.argument('filename',
	type=click.Path(exists=False, file_okay=True, dir_okay=False), default='')
def fetch(system, alternates, game, dest_path, filename):
	'''Fetches box art from "The Cover Project" for the specified game.'''

	# Validate option combinations and arguments.
	if alternates and filename != '':
		print('Cannot get alternate files with specific files or filenames')
		exit(1)

	result = fetch_box_art(system, game, dest_path, filename, alternates)

	exit(0 if result == True else 1)

@abat.command('crop')
@click.option('-s', '--side',
	type=click.Choice(["front", "back"], case_sensitive=False),
		default="front", show_default=True)
@click.argument('source_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.Path(file_okay=True, dir_okay=False))
def crop(side, source_file, dest_file):
	'''Crops a front or back cover from the specified box art image.'''
	try:	
		cover = create_cropped_image(
			side.lower(), source_file, ASPECT_RATIO)
		cover.save(dest_file, "PNG", optimize=True)
		exit(0)
	except Exception as e:		
		exit(1)

@abat.command('resize')
@click.option('-p', '--pad', is_flag=True, default=False,
	help="Adds transparent padding at top and bottom of cover")
@click.argument('source_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.Path(file_okay=True, dir_okay=False))
def resize(pad, source_file, dest_file):
	'''Resizes a cover image to the standard size for the AGSP.'''
	try:
		# Load the soruce image.
		source_image = Image.open(source_file)

		# Adjust sizes and position as needed for padding.
		top, resize_height = get_padding_and_height(pad)

		# Resize the image and save it.
		resized_image = create_resized_image( source_image, top, resize_height)
		resized_image.save(dest_file, "PNG", optimize=True)

		exit(0)
	except Exception as e:
		exit(1)

def create_resized_image(source_image, top, resize_height):
	'''Creates a new, resized, image from a source image and position.'''
	new_image = Image.new("RGBA",
			(COVER_WIDTH, COVER_HEIGHT), color=(255,0,0,0))
	resized_image = source_image.resize((COVER_WIDTH, resize_height),
			Image.Resampling.LANCZOS)	
	new_image.paste(resized_image, (0, top))
	return new_image

def get_padding_and_height(pad):
	'''Gets the padding and height values for an image, based on whether padding
	is enabled or not.'''	
	if pad:
		top = int((COVER_HEIGHT - CROP_HEIGHT) / 2)
		resize_height = CROP_HEIGHT
	else:
		top = 0
		resize_height = COVER_HEIGHT

	return top, resize_height

def create_cropped_image(side, source_file, aspect_ratio):
	'''Creates a new image, cropped for the front or back cover, at the
	specified aspect ratio.'''	
	image = Image.open(source_file)
	return crop_image_for_side(side, image, aspect_ratio)		
	
def crop_image_for_side(side, image, aspect_ratio):
	'''Crops the front or back image from the main image.'''
	crop_box = get_crop_box_for_side(side, image, aspect_ratio)
	return image.crop(crop_box)

def get_crop_box_for_side(side, image, aspect_ratio):
	'''Calculates the crop box for the front or back cover for a given image
	and aspect ratio.'''	
	image_height = image.size[HEIGHT]
	image_width = image_height * aspect_ratio

	if side == FRONT_OPTION:
		# The FRONT crop box is set from the top-right of the image, due to the
		# way box scans are done on "The Cover Project".
		left = image.size[WIDTH] - image_width
		upper = 0
		right = image.size[WIDTH] - 1 
		lower = image.size[HEIGHT] - 1
	else:
		left = 0
		upper = 0
		right = image_width - 1
		lower = image_height - 1

	return (left, upper, right, lower)

def fetch_box_art(system, game, dest_path, filename, include_alternates):
	'''Fetches one, or more, box art files for the specified game and system'''
	# Get a "RAW" name for the game suitable for TCP's CDN.
	raw_name = determine_raw_name(game)
		
	# Build the system_url.  This is the base URL for the target CDN for the
	# specified system, and isthe same for all subsequent operations.
	system_url = get_system_url(system)
	
	# Consider this operation successful if ANY files are downloaded, either
	# primary or alternate since we cannot tell if/how many there are.  This
	# means once result = True we do not change its value again.
	any_file_downloaded = False

	# Iterate possible source file names, based on the name of the game, and
	# the *possible* presence of a "system" prefix (e.g. 'a' for Atari).
	for prefix in SYSTEM_PREFIXES:
		try:
			base_url = f'{system_url}{prefix}{system}_{raw_name}'
			dest_filename, dest_ext = build_dest_filename_and_ext(
				dest_path, SOURCE_PREFIX, system, filename, game)				
			urlretrieve(f'{base_url}{SOURCE_FILE_EXT}',
				f'{dest_filename}{dest_ext}')			
			any_file_downloaded = True		

		except Exception as e:
			pass		

		if include_alternates:
			if fetch_alternate_box_art(base_url, dest_filename, MAX_ALTERNATES):
				# Capture that ANY file has been downloaded.  We don't reset
				# the value if subsequent attempts fail, as there may only be
				# one file.
				any_file_downloaded = True

	return any_file_downloaded

def fetch_alternate_box_art(base_url, dest_filename, max_alternates):
	'''Retrieves up to max_alternatives number of alternate box_art images.'''	

	result = False

	# Retrieve alternate covers until we hit our maximum, or there are
	# no more to retrieve (i.e., we hit an error)
	try:				
		for n in range(FIRST_ALTERNATE, max_alternates + FIRST_ALTERNATE):
			alternate_url = f'{base_url}_{n}'			
			urlretrieve(f'{alternate_url}{SOURCE_FILE_EXT}',
				f'{dest_filename}_{n}{SOURCE_FILE_EXT}')
			result = True

	except Exception as e:
		pass
	
	return result

def determine_raw_name(game):
	'''Determines whether to use the literal, explicit, name supplied, or to
	   interpret the name as a the name of the GAME we want, and adjust it.'''
	return game.translate({ord(i): None for i in INVALID_NAME_CHARS}).lower()	

def build_dest_filename_and_ext(dest_path, prefix, system, filename, game):
	'''Builds a destination filename and extension, based on the path, prefix,
	sytem, game and filenames (if present).'''
	if filename is None or len(filename) == 0:
		dest_file = Path(dest_path) / Path(f'{prefix}{system}_{game}')
		return dest_file, SOURCE_FILE_EXT		
	else:
		return Path(dest_path) / Path(filename), ''		

def get_system_url(system):
	'''Base part of the CDN's url up to, and including, the Atari system'''
	return f'{CDN_BASE}{SYSTEM_BASE}{system}/'

# Run!
if __name__ == '__main__':
    abat()