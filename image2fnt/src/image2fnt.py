#!python3

# image2fnt.py - Bitmapped Image to Atari 8-bit Font Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# 3rd Party/External Modules
import click

# Local Application Modules
import info

# Command Line Interface
@click.group()
@click.version_option(version='0.1.0')
def image2fnt():
    '''Converts bitmapped images to Atari 8-bit .FNT files.'''
    pass

# Run!
if __name__ == '__main__':
    image2fnt.add_command(info.info)    
    image2fnt()