#!python3

# convert.py - Conversion Module for Font to Data Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# 3rd Party/External Modules
import click

# Constants

# Character Set Constants
CHARS_PER_SET = 128

# Common PREFIXES
PREFIX_HEX = '$'
PREFIX_DECIMAL = ''
DEFAULT_SEPARATOR = ','
DEFAULT_PREFIX_BINARY = '~'

# Atari BASIC Constants
BASIC_MAX_LINE_NUMBER = 32767
BASIC_MAX_LINE_LENGTH = 120

# Atari Assembler/Editor Constants
ATARI_ASM_MAX_LINE_NUMBER = 65535
ATARI_ASM_MAX_LINE_LENGTH = 106

# OSS MAC/65 Assembler/Editor Constants
MAC65_MAX_LINE_NUMBER = 65535
MAC65_MAX_LINE_LENGTH = 106
MAC65_BINARY_PREFIX = DEFAULT_PREFIX_BINARY

# MADS Constants
MADS_BINARY_PREFIX = '%'

# Format CONSTANTS
FORMAT_HEX = 'HEX'
FORMAT_DECIMAL = 'DEC'
FORMAT_BINARY = 'BIN'

# Command Line Interface

@click.group()
def convert():
    '''Convert .FNT file to data statements for various Assemblers.'''
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
    '''Convert .FNT file to .BYTE statements for the Atari Assembler.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_atari_asm(bytes, line_number, increment, format.upper()):
        dest_file.write(f'{l}\n') 

@convert.command('atasm')
@click.option('-b', '--bytes_per_line', show_default=True,
    type=click.Choice(['1', '8', '16', '32']) , default='16',
    help='Number of bytes per line.')
@click.option('-f', '--format', show_default=True, default=FORMAT_HEX,
    type=click.Choice([FORMAT_HEX, FORMAT_DECIMAL, FORMAT_BINARY],
    case_sensitive=False), help='Output format for the .BYTE statements.')
@click.option('-s', '--separator', show_default=True, default=DEFAULT_SEPARATOR,
    help='Separator between bytes; use " " for spaces or ", " etc.')
@click.argument('font_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.File('w'), default='-')
def atasm(bytes_per_line: str, format: str, separator: str,
    font_file: str, dest_file):
    '''Convert .FNT file to .BYTE statements for the ATASM Assembler.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_atasm(bytes, int(bytes_per_line), format.upper(), separator):
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
    '''Convert .FNT file to DATA statements for Atari BASIC.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_basic(bytes, line_number, increment):
        dest_file.write(f'{l}\n')

@convert.command('ca65')
@click.option('-b', '--bytes_per_line', show_default=True,
    type=click.Choice(['1', '8', '16', '32']) , default='16',
    help='Number of bytes per line.')
@click.option('-f', '--format', show_default=True, default=FORMAT_HEX,
    type=click.Choice([FORMAT_HEX, FORMAT_DECIMAL, FORMAT_BINARY],
    case_sensitive=False), help='Output format for the .BYTE statements.')
@click.option('-s', '--separator', show_default=True, default=DEFAULT_SEPARATOR,
    help='Separator between bytes; use " " for spaces or ", " etc.')
@click.argument('font_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.File('w'), default='-')
def atasm(bytes_per_line: str, format: str, separator: str,
    font_file: str, dest_file):
    '''Convert .FNT file to .BYTE statements for the CA65 Assembler.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_ca65(bytes, int(bytes_per_line), format.upper(), separator):
        dest_file.write(f'{l}\n')         

@convert.command('mac65')
@click.option('-l', '--line_number', show_default=True, type=int, default=1000,
    help='Starting line number for .BYTE statements.')
@click.option('-i', '--increment', show_default=True, type=int, default=10,
    help='Increment between line numbers.')
@click.option('-f', '--format', show_default=True, default=FORMAT_HEX,
    type=click.Choice([FORMAT_HEX, FORMAT_DECIMAL, FORMAT_BINARY],
    case_sensitive=False), help='Output format for the .BYTE statements.')
@click.argument('font_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest_file', type=click.File('w'), default='-')
def atari(line_number: int, increment: int, format: str, font_file: str,
    dest_file):
    '''Convert .FNT file to .BYTE statements for the OSS MAC/65 Assembler.'''
    f = open(font_file, 'rb')
    bytes = f.read()
    for l in to_mac65(bytes, line_number, increment, format.upper()):
        dest_file.write(f'{l}\n')   

# Core Functions
def to_atari_asm(bytes: list, first_line_number: int, increment: int,
    format) -> list:
    '''Convert the bytes to line-numbered .BYTE statements for the Atari
    Assembler/Editor.'''
    prefix = PREFIX_HEX if format == 'HEX' else PREFIX_DECIMAL
    return to_line_numbered_data(bytes, first_line_number, increment,
        ATARI_ASM_MAX_LINE_NUMBER, ATARI_ASM_MAX_LINE_LENGTH,
        '.BYTE', prefix, format)

def to_atasm(bytes: list, bytes_per_line: int, format: str,
    seperator: str) -> list:
    '''Convert the bytes to .BYTE statements for the ATASM Assembler.'''
    prefix = prefix_from_format(format)
    return to_data(bytes, bytes_per_line, '.BYTE', prefix, format,
        seperator)

def to_basic(bytes: list, first_line_number: int, increment: int) -> list:
    '''Convert the bytes to line-numbered DATA statements for Atari BASIC.'''
    return to_line_numbered_data(bytes, first_line_number, increment,
        BASIC_MAX_LINE_NUMBER, BASIC_MAX_LINE_LENGTH, 'DATA',
        PREFIX_DECIMAL,FORMAT_DECIMAL)

def to_ca65(bytes: list, bytes_per_line: int, format: str,
    seperator: str) -> list:
    '''Convert the bytes to .BYTE statements for the CA65 Assembler.'''
    prefix = prefix_from_format(format)
    return to_data(bytes, bytes_per_line, '.BYTE', prefix, format,
        seperator)

def to_mac65(bytes: list, first_line_number: int, increment: int,
    format) -> list:
    '''Convert the bytes to line-numbered .BYTE statements for the OSS MAC/65
    Assembler/Editor.'''
    # Determine data type prefix
    prefix = prefix_from_format(format)

    return to_line_numbered_data(bytes, first_line_number, increment,
        MAC65_MAX_LINE_NUMBER, MAC65_MAX_LINE_LENGTH, '.BYTE', prefix, format)

def to_line_numbered_data(bytes: list, first_line_number: int, increment: int,
    max_line_number: int, max_line_length: int, directive: str, prefix: str,
    format: str ) -> list:
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
            #line += (f'${bytes[index]:02X},' if format == 'HEX'
            #         else f'{bytes[index]},')
            line += formatted_value(bytes[index], prefix, format)
            line += DEFAULT_SEPARATOR
            index += 1
        
        # Remove trailing comma, add line to the list and move to next line
        line = line.rstrip(DEFAULT_SEPARATOR)
        lines.append(line)       
        line_number += increment  
    
    return lines

def next_item_length(byte: int, format: str, add_space: bool) -> int:
    '''Return the length of the next item in the format specified.'''
    if format.upper() =='HEX':
        return 4 if add_space else 3
    else:
        return len(f'{byte}') + (1 if add_space else 0)

def to_data(bytes: list, bytes_per_line: int, directive: str, prefix: str,
        format: str, separator: str) -> list:
    '''Convert the bytes to .BYTE, dta or .HE statements for various assemblers
    based on the formatting arguments provided.'''
    lines = []
    num_lines = int(len(bytes) / bytes_per_line)
    for line_num in range(num_lines):
        bytes_for_line = bytes[line_num * bytes_per_line:
                               (line_num * bytes_per_line) + bytes_per_line]
        line = f'{directive} '
        for byte in bytes_for_line:
            line += formatted_value(byte, prefix, format)
            line += separator
        
        # Remove trailing comma, add line to the list and move to next line
        line = line.rstrip(separator)
        lines.append(line)
            
    return lines

def formatted_value(byte: int, prefix:str, format: str) -> str:
    '''Return the formatted value of the byte based on the format argument.'''
    value = f'{prefix}'
    # Can't use match/case due to FORMAT_ contants being capture patterns
    if format.upper() == FORMAT_HEX:
        value += f'{byte:02X}'
    elif format.upper() == FORMAT_DECIMAL:
        value += f'{byte}'
    elif format.upper() == FORMAT_BINARY:
        value += f'{byte:08b}'
    else:
        raise ValueError('Invalid format argument.')
    return value

def prefix_from_format(format: str) -> str:
    '''Return the prefix for the format argument.'''
    format = format.upper()
    if format == FORMAT_HEX:
        return PREFIX_HEX
    elif format == FORMAT_DECIMAL:
        return PREFIX_DECIMAL
    elif format == FORMAT_BINARY:
        return DEFAULT_PREFIX_BINARY
    else:
        raise ValueError('Invalid format argument.')    
# Run!
if __name__ == '__main__':
    convert()