#!python3

# info.py - Image Info display for Image to Font Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
from sys import argv

# 3rd Party/External Modules
import click
from PIL import Image

# Constants

# Palette Constants
RGB_BANDS = 'RGB'

# Color Constants
COUNT_INDEX = 0
COLOR_INDEX = 1

# Image Constants
WIDTH_INDEX = 0
HEIGHT_INDEX = 1

# Character Constants
BITS_PER_CHAR = 8
BYTES_PER_CHAR = 8

# Command Line Interface

@click.command('info')
@click.option('-a', '--aspect_ratio', show_default=True, default='1:1',
	type=click.Choice(['1:1', '2:1']), help='Pixel aspect ratio.')
@click.argument('filename',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
def info(aspect_ratio: str, filename: str):
	'''Displays image size, color/palette data, and possible character layouts.'''
	im = Image.open(filename)

	# Do BANDS ... (not sure if we'll need this)
	# Might just be something I need to determine how to decode colors if the
	# image is not paletted.
	print("BANDS:")
	for b in im.getbands():
		print(b)

	display_image_details(im)


	print()
	# Do COLOR and PALETTE stuff.
	palette = im.getpalette(None)

	if palette == None:
		print(f'This image/format does not use a palette.  RGB color values are '
			  f'used directly, instead.\n')

		colors = im.getcolors()
		for color in colors:
			print(f'Count: {color[COUNT_INDEX]:>04} -> '
				  f'RGB: ${RGB_from_color(color[COLOR_INDEX])}')
	else:
		print(f'PALETTE:')
		print(palette)
		print()
		display_palette(im)

def RGB_from_palette_index(palette: list[int], index: int) -> str:
	'''Gets a HEX formatted RGB COLOR value for a paletted color INDEX'''
	band = index * len(RGB_BANDS)
	return f'{palette[band]:02X}{palette[band+1]:02X}{palette[band+2]:02X}'

def display_palette(image: Image):
	'''Displays the USED palette color INDEXes, their count and RGB color'''
	palette = image.getpalette(None)
	# We don't care about PALETTE INDEXES that are not used in the image
	# so only show those that ARE used - which will have representative entries
	# in the COLORS collection.
	colors = image.getcolors()
	for palette_index in range(len(colors)):		
		print(f'Index: {palette_index:>03} * {colors[palette_index][0]:>04} -> '
			  f'RGB: ${RGB_from_palette_index(palette, palette_index)}')

def RGB_from_color(color: tuple[int, int, int]) -> str:
	'''Gets a HEX formatted RGB COLOR value for the specified COLOR tuple'''
	return f'{color[0]:02X}{color[1]:02X}{color[2]:02X}'

def display_image_details(image: Image):
	print("Image Details:\n")

	width, height = image.size
	print(f'  Image SIZE: {width} W x {height} H pixels')
	chars_per_row = int(width / BITS_PER_CHAR)
	rows = int(height / BYTES_PER_CHAR)
	print(f'    Contains: {rows} rows of {chars_per_row} characters')
	print(f' Total Chars: {rows * chars_per_row}')	



# Run!
if __name__ == '__main__':
    if len(argv) == 1:
        info(['--help'])
    else:
        info()