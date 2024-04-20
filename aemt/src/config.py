# config.py - Atari THE400 Mini Configuration Utility & Functions
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules

import enum
import pathlib
from typing import Self

# 3rd Party/External Modules
import click

# Constants

# Error Messages and Command Result Exit Codes
ERROR_TEXT ='Error: '
ERROR = 1
SUCCESS = 0

# Verbosity Values
SILENT = 0
PROGRESS = 1
VERBOSE = 2

# THE400 Mini CONFIG Constants

# Controller Defaults
CONTROLLER_DEFAULTS = {'a':'joy_a', 'b':'start', 'x':'option', 'y':'select',
	'up':'joy_up', 'down':'joy_down', 'left':'joy_left', 'right':'joy_right',
	'sl':'joy_a', 'sr':'joy_a', 'menu':'option'}

CONTROLLER_5200_DEFAULTS = {'a':'joy_a', 'b':'5200_start', 'x':'option',
	'y':'5200_pause', 'up':'axis_left_y', 'down':'axis_left_y',
	'left':'axis_left_x', 'right':'axis_left_x', 'sl':'joy_a', 'sr':'joy_a',
	'menu':'option'}

CONTROLLER_PREIX = 'controller_'
CONTROLLER_SEPARATOR = '_'
NUMBER_OF_CONTROLLERS = 4

# Display Defaults
DEFAULT_DISPLAY_START = 20
DEFAULT_DISPLAY_HEIGHT = 200
DEFUALT_DISPLAY_WIDTH = 320

# Machine Defaults
DEFAULT_MODEL = 'XE'

@click.group()
@click.version_option('0.0.0.1')
def config():
    '''Creates and updates .CFG files for THE400 Mini USB Media games.'''
    pass

@config.command()
@click.option('-m', '--model', default=DEFAULT_MODEL, show_default=True,
	type=click.Choice(['400', '800', 'XL', 'XE', '5200']),
	help='Atari 8-bit Model to configure for (where XL=800XL and XE=130XE)')
@click.option('-b', '--basic', is_flag=True, default=False, help="Enable BASIC")
@click.option('-vs', '--video_std', type=click.Choice(['NTSC', 'PAL']),
	default="NTSC", show_default=True,
	help='Video Standard (NTSC=60Hz, PAL=50Hz)')
@click.option('-p', '--force_pal', is_flag=True, default=False,
	help='Forces PAL operation (60Hz refresh)')
@click.option('-a', '--artefact', default='0', show_default=True,
	type=click.Choice(['0','1','2','3']), help="Artefacting mode")
@click.option('-s', '--start', default=DEFAULT_DISPLAY_START, show_default=True,
	help='Display Start scanline (lower values start higher on screen)')
@click.option('-h', '--height', default=DEFAULT_DISPLAY_HEIGHT,
    show_default=True, help='Display Height (scanlines)')
@click.option('-w', '--width', default=DEFUALT_DISPLAY_WIDTH, show_default=True,
	help='Display Width (pixels)')
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
    default='1', show_default=True, help='Status/progress reporting verbosity')
def config(model: str, basic: bool, video_std: str, force_pal: bool,
	artefact: str, start: int, height: int, width: int,verbosity: str):
	'''Creates .cfg files for Atari THE400 Mini.'''
	print(model)

# Run!
if __name__ == '__main__':
    config()