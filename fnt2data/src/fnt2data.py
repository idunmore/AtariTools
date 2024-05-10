#!python3

# fnt2data.py - Font to Data Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# 3rd Party/External Modules
import click

# Command Line Interface

@click.group()
@click.version_option(version='0.1.0')
def fnt2data():
    '''Converts Atari 8-bit .FNT files to data blocks for various Assemblers.'''
    pass

@fnt2data.command('show')
@click.option('-b', '--border', is_flag=True, default=False,
        help='Display a border around each character.')
@click.option('-c', '--chars_per_line', show_default=True,
        type=click.Choice(['1', '8', '16']), default='8',
        help='Number of characters to display per line.')
@click.argument('filename',
	type=click.Path(exists=True, file_okay=True, dir_okay=False), default='')
def show(border: bool, chars_per_line: int, filename: str):
    '''Graphically displays the all characters defined in the .FNT file.'''
    pass

@fnt2data.command('convert')
@click.option('-t', '--target', show_default=True, default='MADS',
        type=click.Choice(['Atari', 'ATASM', 'CA65', 'MAC65', 'MADS', 'BASIC'],
            case_sensitive=False), help='Target Assembler or BASIC version.')
@click.option('-f', '--format', show_default=True, default='HEX',
        type=click.Choice(['HEX', 'DEC', 'BIN'], case_sensitive=False),
        help='Output format for the data.')
@click.option('-s', '--separator', show_default=True, default='Comma',
        type=click.Choice(['Comma', 'Space'], case_sensitive=False),
        help='Separator character between data values.')
@click.option('-d', '--directive', show_default=True, default='BYTE',
        type=click.Choice(['BYTE', 'HE', 'dta', 'DATA'], case_sensitive=False),
        help='Assembler or BASIC "DATA" directive for the data.')
@click.argument('source_file',
	type=click.Path(exists=True, file_okay=True, dir_okay=False), default='')
@click.argument('dest_file',
	type=click.Path(exists=False, file_okay=True, dir_okay=False), default='')
def convert(target: str, format: str, separator: str, source_file: str,
        dest_file: str):
    '''Convert the .FNT file to data blocks for various Assemblers.'''
    pass


# Run!
if __name__ == '__main__':
    fnt2data()