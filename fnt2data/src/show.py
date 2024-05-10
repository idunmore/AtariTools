#!python3

# show.py - Show Module for Font to Data Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
from sys import argv

# 3rd Party/External Modules
import click

# Display Constants - Unicode Box and Block Drawing Characters
CHAR_BLOCK = chr(9608)
BOX_MIDDLE_LEFT = chr(9500)
BOX_MIDDLE_RIGHT = chr(9508)
BOX_MIDDLE = chr(9472)
BOX_TOP_LEFT = chr(9484)
BOX_TOP_RIGHT = chr(9488)
BOX_BOTTOM_LEFT = chr(9492)
BOX_BOTTOM_RIGHT = chr(9496)
BOX_VERTICAL = chr(9474)

# Character Set/FNT (Font) Constants
CHARS_PER_SET = 128
BYTES_PER_CHAR = 8
CHAR_BIT_WIDTH = 8

# Command Line Interface

@click.command('show')
@click.option('-b', '--border', is_flag=True, default=False,
        help='Display a border around each character.')
@click.option('-c', '--chars_per_line', show_default=True,
        type=click.Choice(['1', '8', '16']), default='8',
        help='Number of characters to display per line.')
@click.argument('filename',
	type=click.Path(exists=True, file_okay=True, dir_okay=False), default='')
def show(border: bool, chars_per_line: int, filename: str):
    '''Graphically displays the all characters defined in the .FNT file.'''
    with open(filename, 'rb') as f:
        bytes = f.read()
        show_font(bytes, border, int(chars_per_line))

# Main Functions

def show_font(bytes: list, border: bool, chars_per_line: int):
    '''Display the characters in the font file.'''
    # Set left and right box characters based on border flag.
    left = BOX_VERTICAL if border else ''
    right = BOX_VERTICAL if border else ''    
    
    print_border(f'{BOX_TOP_LEFT}{BOX_MIDDLE * CHAR_BIT_WIDTH}{BOX_TOP_RIGHT}'
          * chars_per_line, border)

    # Display each line of characters.
    lines = int(CHARS_PER_SET / chars_per_line)
    for line in range(lines):

        # Don't attempt to print a border, even if enabled, for the first line.
        if line > 0:
            print_border(
                f'{BOX_MIDDLE_LEFT}{BOX_MIDDLE * CHAR_BIT_WIDTH}'
                f'{BOX_MIDDLE_RIGHT}' * chars_per_line, border)
            
        # Build up a bitmap for all of the characters on this line
        # one vertical character-byte at a time.        
        for char in range(BYTES_PER_CHAR):
            bitmap = ''
            for byte in range(chars_per_line):
                # Calculate the offset into the font data for the character and
                # scan-line within it, we are currently processing.
                offset = ((line * BYTES_PER_CHAR * chars_per_line) +
                          (byte * BYTES_PER_CHAR) + char)
                
                # Add the character-line bitmap, with appropraite left/right
                # borders, to build out the whole line.
                bitmap += f'{left}{get_bitmap(bytes[offset])}{right}'            
            print(bitmap)

    print_border(
        f'{BOX_BOTTOM_LEFT}{BOX_MIDDLE * CHAR_BIT_WIDTH}{BOX_BOTTOM_RIGHT}'
        * chars_per_line, border)
        
def get_bitmap(byte: int) -> str:
    '''Gets a binary version of the byte, and swaps the 0's for SPACE and 1's
    for a block character.'''
    binary = f'{byte:>08b}'
    binary = binary.replace('0', ' ')
    binary = binary.replace('1', CHAR_BLOCK)
    return binary

def print_border(line: str, border: bool):
    '''Print a border line if the border flag is set.'''
    if border:
        print(line)
    
# Run!
if __name__ == '__main__':
    if len(argv) == 1:
        show(['--help'])
    else:
        show()