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

# Exit Codes
ERROR = 1
SUCCESS = 0

SEPARATOR = ','
BIT_PATTERNS = [0b00, 0b01, 0b10, 0b11]
BYTES_PER_CHARACTER = 8
EVERY_PIXEL = 1
EVERY_OTHER_PIXEL = 2

# Color Constants
MAX_COLORS = 4
RED_INDEX = 0
GREEN_INDEX = 1
BLUE_INDEX = 2

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
    try:
        # Open the source image file.
        image = Image.open(image_file)

        # Setup all the parameters for the conversion.
        pixels_per_character = get_pixels_per_character(aspect_ratio)
        bit_mapping = get_bit_mapping(image, colors)   
        pixel_step = get_pixel_step(len(bit_mapping), pixels_per_character)
        width, height = image.size

        # Do the conversion ...
        output_bytes = do_conversion(image, pixels_per_character, bit_mapping,
            pixel_step, width, height)

        image.close()

        # ... and write the output to the specified file:
        with open(fnt_file, 'wb') as output_file:
            output_file.write(bytes(output_bytes))

        exit(SUCCESS)
    
    except Exception as e:
        print(f'Error: {e}')
        exit(ERROR)

def do_conversion(image: Image, pixels_per_character: int,
    bit_mapping: dict[str, int], pixel_step: int, width: int, height: int,
    ) -> list[int]:
    '''Converts source file, based on parameters, and returns it as a list
    of bytes.'''
    
    # For 8-bit, 2 color (the number of bit maps = the number of colors) images
    # we shift 1 bit per pixel ...
    if pixels_per_character == 8 and len(bit_mapping) == 2:
        bits_to_shift = 1
    else:
        # ... otherwise we're dealing with 2:1 aspect ratios or 4-color images
        # which require 2-bits per pixel.
        bits_to_shift = 2

    output_bytes = []
    # For every row of characters in the source image ...
    for row in range(height // BYTES_PER_CHARACTER):
        # ... process each character from left to right ...
        for character in range(width // pixels_per_character):
            # ... doing all 8 vertical bytes at a time ...           
            for byte in range(BYTES_PER_CHARACTER):
                output_byte = 0
                # ... add the output bits for each pixel in the character ...
                for pixel in range(0, pixels_per_character, pixel_step):
                    # Get X and Y coordinates for the pixel in the source image.
                    x = (character * pixels_per_character) + pixel
                    y = (row * BYTES_PER_CHARACTER) + byte
                    # Get the pixel value, create output bit pattern lookup key.
                    key = get_key_from_pixel_or_color(image.getpixel((x, y)))
                    
                    # Shift the output byte left and add the bit pattern.
                    # Initial value is 0, so we can always shift on the first
                    # pass, without needing "first iteration" logic.                 
                    output_byte = output_byte << bits_to_shift                   
                    output_byte += bit_mapping[key] 

                # Add the output byte to the list of output bytes.
                output_bytes.append(output_byte)

    return output_bytes                     
            
def get_pixel_step(number_of_bit_maps: int, pixels_per_character: int) -> int:
    '''Returns the number of pixels to step through for each character.'''
    # For 2-color or wide-aspect characters in the SOURCE, we process every
    # pixel, since there is either 8 of them, or they're assumed to be 2 bits
    # wide.  For 4-color characters, in standard aspect ration, each source
    # pixel is repeated twice, so we only process every other one.
    if number_of_bit_maps == 2 or pixels_per_character == 4:
        return EVERY_PIXEL
    else:
        return EVERY_OTHER_PIXEL

def get_pixels_per_character(aspect_ratio: str) -> int:
    '''Returns the number of pixels per character based on the aspect ratio.'''
    # If the aspect ratio is not 2:1, then it means that a SINGLE pixel in the
    # source file is actually 2 pixels wide for display, so we process half
    # as many on the INPUT (they will be double-wide in the OUTPUT.)
    return 4 if aspect_ratio == '2:1' else 8   

def get_bit_mapping(image: Image, colors: str) -> dict[str, int]:
    '''Returns the color to bitmap mapping for the specified image, based on
    the colors or indexes specified. If no colors are specified, then default'''
    if colors == None:
        return get_default_color_to_bit_mapping(image)
    else:
        return get_color_to_bit_mapping(colors)

def get_default_color_to_bit_mapping(image: Image) -> dict[str, int]:
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

def get_color_to_bit_mapping(colors: str) -> dict[str, int]:
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