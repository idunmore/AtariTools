#!python3

# convert.py - Conversion Module for Image to Font Converter
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

SEPARATOR = ','
BIT_PATTERNS = ['00', '01', '10', '11']

# Band and Palette Constants
RGB_BANDS = 'RGB'

# Color Constants
MAX_COLORS = 4
RED_INDEX = 0
GREEN_INDEX = 1
BLUE_INDEX = 2

FREQUENCY_INDEX = 0
COLOR_INDEX = 1

# Command Line Interface

@click.command('convert')
@click.option('-c', '--colors', show_default=False, default=None,
    help=f'Color/index assignements for %00, %01 [and %10, %11] bit-outputs '
         f'(e.g., -c "FFFFFF,000000" for RGB colors or '
         f'-c "#0,#1," for palette indexes).')
@click.option('-a', '--aspect_ratio', show_default=True, default='1:1',
	type=click.Choice(['1:1', '2:1']), help='Pixel aspect ratio.')
@click.argument('image_file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('fnt_file',
    type=click.Path(exists=False, file_okay=True, dir_okay=False))
def convert(colors: str, aspect_ratio: str, image_file: str, fnt_file: str):
    '''Converts bitmapped images to Atari 8-bit .FNT files.'''
    image = Image.open(image_file)
    print(get_bit_mapping(image, colors))

def get_bit_mapping(image: Image, colors: str) -> dict[str, str]:
    '''Returns the color to bitmap mapping for the specified image, based on
    the colors or indexes specified. If no colors are specified, then default'''
    if colors == None:
        return get_default_color_to_bit_mapping(image)
    else:
        return get_color_to_bit_mapping(colors)

def get_default_color_to_bit_mapping(image: Image) -> dict[str, str]:
    '''Returns the default color to bitmap mapping (no -color specified).'''
    mapping = {}
    colors = image.getcolors()    
    # Default is simply to map the first 4 colors to the first 4 bit patterns.
    number_of_colors = min(MAX_COLORS, len(colors))
    for index in range(number_of_colors):
        # Handes pixel value as either colors or palette indexes automatically.
        key = get_key_from_pixel_or_color(colors[index][COLOR_INDEX])
        mapping[key] = BIT_PATTERNS[index]        
       
    return mapping

def get_color_to_bit_mapping(colors: str) -> dict[str, str]:
    '''Returns a dictionary mapping color values or indexes to their output
    bitmaps.'''
    entries = colors.split(SEPARATOR)
    if len(entries) > MAX_COLORS:
        raise ValueError(f'Only {MAX_COLORS} colors are supported.')
    
    mapping = {}
    # Build the mapping list, for each entry in the color entries list.    
    for index in range(len(entries)):
        if entries[index][0] == '#':
             # This is a palette index (remove the '#' index prefix).
            mapping[str(int(entries[index][1:]))] = BIT_PATTERNS[index]
        else:   
            # This is a direct RGB color value.
            mapping[entries[index]] = BIT_PATTERNS[index]

    return mapping  

def get_key_from_pixel_or_color(pixel: tuple[int, int, int] | int) -> str:
    '''Returns the key for the pixel, it's color value or index.'''
    if type(pixel) is tuple:
        # Pixel is an RGB tuple.   
        return RGB_from_pixel(pixel)
    else:
        # Pixel is a palette index.
        return str(pixel)

def RGB_from_pixel(pixel: tuple[int, int, int]) -> str:
	'''Gets a HEX formatted RGB COLOR value for the specified pixel'''
	return (f'{pixel[RED_INDEX]:02X}'
		 	f'{pixel[GREEN_INDEX]:02X}'
			f'{pixel[BLUE_INDEX]:02X}')

# Run!
if __name__ == '__main__':
    if len(argv) == 1:
        convert(['--help'])
    else:
        convert()