#!python3

# convert.py - Conversion Module for Font to Data Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
from sys import argv

# 3rd Party/External Modules
import click

# Constants

# Atari BASIC Constants
BASIC_MAX_LINE_NUMBER = 32767
BASIC_MAX_LINE_LENGTH = 120

# Atari Assembler/Editor Constants
ATARI_ASM_MAX_LINE_NUMBER = 65535
ATARI_ASM_MAX_LINE_LENGTH = 106

# Format CONSTANTS
FORMAT_HEX = 'HEX'
FORMAT_DECIMAL = 'DEC'
FORMAT_BINARY = 'BIN'

# Command Line Interface

@click.group()
def convert():
    '''Convert a .FNT file to data statements for various Assemblers.'''
    pass

@convert.command('atari')
@click.option('-l', '--line_number', show_default=True, type=int, default=1000,
    help='Starting line number for .BYTE statements.')
@click.option('-i', '--increment', show_default=True, type=int, default=10,
    help='Increment between line numbers.')
@click.option('-f', '--format', show_default=True, default=FORMAT_HEX,
    type=click.Choice([FORMAT_HEX, FORMAT_DECIMAL], case_sensitive=False),
    help='Output format for the .BYTE statements.')
@click.argument('font_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.File('w'), default='-')
def atari(line_number: int, increment: int, format: str, font_file: str,
    dest_file):
    '''Convert the .FNT file to .BYTE statements for the Atari Assembler.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_atari_asm(bytes, line_number, increment, format):
        dest_file.write(f'{l}\n')   

@convert.command('basic')
@click.option('-l', '--line_number', show_default=True, type=int, default=1000,
    help='Starting line number for DATA statements.')
@click.option('-i', '--increment', show_default=True, type=int, default=10,
    help='Increment between line numbers.')
@click.argument('font_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.File('w'), default='-')
def basic(line_number: int, increment: int, font_file: str, dest_file):
    '''Convert the .FNT file to DATA statements for Atari BASIC.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_basic(bytes, line_number, increment):
        dest_file.write(f'{l}\n')

# Core Functions
def to_atari_asm(bytes: list, first_line_number: int, increment: int,
    format) -> list:
    '''Convert the bytes to line-numbered .BYTE statements for the Atari
    Assembler/Editor.'''
    return to_line_numbered_data(bytes, first_line_number, increment,
        ATARI_ASM_MAX_LINE_NUMBER, ATARI_ASM_MAX_LINE_LENGTH, '.BYTE', format)

def to_basic(bytes: list, first_line_number: int, increment: int) -> list:
    '''Convert the bytes to line-numbered DATA statements for Atari BASIC.'''
    return to_line_numbered_data(bytes, first_line_number, increment,
        BASIC_MAX_LINE_NUMBER, BASIC_MAX_LINE_LENGTH, 'DATA', FORMAT_DECIMAL)

def to_line_numbered_data(bytes: list, first_line_number: int, increment: int,
    max_line_number: int, max_line_length: int, directive: str, format: str
    ) -> list:
    '''Convert the bytes to line-numbered data statements for either Atari BASIC
    or the Atari Assembler/Editor.'''
    lines = []
    line_number = first_line_number
    index = 0
    byte_length = len(bytes)

    # Process all bytes into lines of data.
    while(index < byte_length):

        # Ensure line number is legal
        if line_number > max_line_number:
            raise ValueError('Line number exceeds maximum value.')
        
        # Start a new line of data ...
        line = f'{line_number} {directive} '
        # ... adding as many items as will fit within the line length limit
        while(index < byte_length and len(line) <=
              (max_line_length - next_item_length(bytes[index], format, False))
             ):
            # Add the next byte to the line
            line += (f'${bytes[index]:02X},' if format == 'HEX'
                     else f'{bytes[index]},')
            index += 1
        
        # Remove trailing comma, add line to the list and move to next line
        line = line.rstrip(',')
        lines.append(line)       
        line_number += increment  
    
    return lines

def next_item_length(byte: int, format: str, add_space: bool) -> int:
    '''Return the length of the next item in the format specified.'''
    if format.upper() =='HEX':
        return 4 if add_space else 3
    else:
        return len(f'{byte}') + (1 if add_space else 0)

# Run!
if __name__ == '__main__':
    convert()