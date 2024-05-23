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

# Command Line Interface

@click.command('convert')
def convert():
    '''Converts bitmapped images to Atari 8-bit .FNT files.'''
    pass

# Run!
if __name__ == '__main__':
    if len(argv) == 1:
        convert(['--help'])
    else:
        convert()