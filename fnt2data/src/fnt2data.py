#!python3

# fnt2data.py - Font to Data Converter
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# 3rd Party/External Modules
import click

# Local Application Modules
import show
import convert

# Command Line Interface
@click.group()
@click.version_option(version='0.1.0')
def fnt2data():
    '''Converts Atari 8-bit .FNT files to data blocks for various Assemblers.'''
    pass

# Run!
if __name__ == '__main__':
    fnt2data.add_command(show.show)
    fnt2data.add_command(convert.convert)
    fnt2data()