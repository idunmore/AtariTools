# AEMT.py - [A]tari [E]ight-bit [M]ulti-[T]ool
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# 3rd Party/External Modules
import click

# Local Application Modules
import split
import cartridge
import config

# Constants

# Error Messages and Command Result Exit Codes
ERROR_TEXT ='Error: '
ERROR = 1
SUCCESS = 0

# Verbosity Values
SILENT = 0
PROGRESS = 1
VERBOSE = 2

# Command Line Interface

@click.group()
@click.version_option('0.0.0.3')
def aemt():
    '''[A]tari [E]ight-bit [M]ulti-[T]ool

            Moves files to organized folder structures, with an optionally
            limited	number of files per folder.

            Fingerprints game images, identifies image file types and creates
            .cfg files for Atari THE400 Mini games on USB media.'''
    pass

# GENERAL Utility Functions

def echo_v(message: str, verbosity: int):
    if verbosity == VERBOSE:
        click.echo(message)	

# Run!
if __name__ == '__main__':
    aemt.add_command(split.split)
    aemt.add_command(cartridge.cart)
    aemt.add_command(config.config)
    aemt()