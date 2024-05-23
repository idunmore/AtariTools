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

# Band and Palette Constants
RGB_BANDS = 'RGB'

# Color Constants
COUNT_INDEX = 0
COLOR_INDEX = 1
FREQUENCY_INDEX = 0
RED_INDEX = 0
GREEN_INDEX = 1
BLUE_INDEX = 2

# Character Constants
BITS_PER_CHAR = 8
BYTES_PER_CHAR = 8

# Command Line Interface

@click.command('info')
@click.argument('filename',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
def info(filename: str):
	'''Displays image metrics, color/palette data, and character layout.'''
	image = Image.open(filename)
	display_details(image)
	image.close()	

# Main Functions

def display_details(image: Image):
	'''Displays the image details, including size and color/palette data'''
	display_image_metrics(image)
		
	palette = image.getpalette()
	if palette == None:
		# This image is not paletted, so we'll display the colors directly.
		display_colors(image)
	else:
		# This image uses a palette, so display its details.
		display_palette(image)

def display_image_metrics(image: Image):
	'''Displays the image metrics, including size and character layout'''
	print(f'    Format: {image.format}')
	width, height = image.size
	print(f'Image Size: {width} W x {height} H (pixels)')
	chars_per_row = int(width / BITS_PER_CHAR)
	rows = int(height / BYTES_PER_CHAR)
	print(f'Characters: {rows * chars_per_row} (in '
	   	  f'{rows} rows of {chars_per_row}) ')
	print(f'     Bands: {get_bands(image)}')

def display_palette(image: Image):
	'''Displays the USED palette color INDEXes, their frequency and RGB color'''
	print(f'\nThis image uses a palette; entries are as follows:\n')
	palette = image.getpalette()
	# We don't care about PALETTE INDEXES that are not used in the image
	# so only show those that ARE used - which will have representative entries
	# in the COLORS collection.
	colors = image.getcolors()
	print(f'Index | RGB Color | Frequency')
	for palette_index in range(len(colors)):		
		print(f' {palette_index:>3}     '
			  f'${RGB_from_palette_index(palette, palette_index)}      '
			  f'{colors[palette_index][FREQUENCY_INDEX]:>5,}')
		
def display_colors(image: Image):
	'''Displays the RGB colors used in the image and their frequency'''
	print(f'\nThis image has no palette; RGB color values are used directly:\n')
	colors = image.getcolors()
	print(f'RGB Color | Frequency')
	for color in colors:
		print(f' ${RGB_from_color(color[COLOR_INDEX])}     '
			  f'{color[COUNT_INDEX]:>5,}')

# Utility and Formatting Functions
def RGB_from_palette_index(palette: list[int], index: int) -> str:
	'''Gets a HEX formatted RGB COLOR value for a paletted color INDEX'''
	band = index * len(RGB_BANDS)
	return (f'{palette[band + RED_INDEX]:02X}'
		 	f'{palette[band + GREEN_INDEX]:02X}'
			f'{palette[band + BLUE_INDEX]:02X}')

def RGB_from_color(color: tuple[int, int, int]) -> str:
	'''Gets a HEX formatted RGB COLOR value for the specified COLOR tuple'''
	return (f'{color[RED_INDEX]:02X}'
		 	f'{color[GREEN_INDEX]:02X}'
			f'{color[BLUE_INDEX]:02X}')

def get_bands(image: Image) -> str:
	'''Gets the Color BANDS used in the image as a single string sequence'''
	return ''.join(band for band in image.getbands())

# Run!
if __name__ == '__main__':
    if len(argv) == 1:
        info(['--help'])
    else:
        info()