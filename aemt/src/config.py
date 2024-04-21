# config.py - Atari THE400 Mini Configuration Utility & Functions
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
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

EOL = ';'

# Emulator Keys & Defaults
KEY_EMULATOR_PREFIX = 'emulator_'
KEY_EMULATOR_MACHINE = 'machine'
KEY_EMULATOR_ARTEFACT = 'artefact'
KEY_EMULATOR_FORCE_PAL = 'force_pal'
DEFAULT_MACHINE = 'XE'
DEFAULT_ARTEFACT = '0'
DEFAULT_FORCE_PAL = 'false'
EMULATOR_SEPARATOR = '-'
BASIC = 'basic'

# Map CLI Model IDs (key) to Config File Machine IDs (value)
MODEL_MACHINE_ID = {'400':'400', '800':'800', 'XL':'800xl', 'XE':'130xe',
                 '5200':'5200'}

# Controller Keys & Defaults
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

KEY_INPUT_ANALOG_PREFIX = 'input_analogue_'
KEY_ANALOG_RATE = 'rate'
KEY_ANALOG_CURVE = 'curve'
KEY_ANALOG_AUTO_CENTER = 'autocenter'
DEFAULT_ANALOG_RATE = 100
DEFAULT_ANALOG_CURVE = 'linear'
DEFAULT_AUTO_CENTER = 'off'

# Display Keys & Defaults

KEY_DISPLAY_PREFIX = 'display_'
KEY_DISPLAY_START = 'start_line'
KEY_DISPLAY_HEIGHT = 'height'
KEY_DISPLAY_WIDTH = 'width'
DEFAULT_DISPLAY_START = 20
DEFAULT_DISPLAY_HEIGHT = 200
DEFAULT_DISPLAY_WIDTH = 320

# Command Line Interface

@click.group()
@click.version_option('0.0.0.1')
def config():
    '''Creates and updates .CFG files for THE400 Mini USB Media games.'''
    pass

@config.command()
@click.option('-m', '--model', default=DEFAULT_MACHINE, show_default=True,
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
@click.option('-w', '--width', default=DEFAULT_DISPLAY_WIDTH, show_default=True,
	help='Display Width (pixels)')
@click.argument('filename', type=click.File('w'), default='-')
def create(filename, model: str, basic: bool, video_std: str, force_pal: bool,
	artefact: str, start: int, height: int, width: int):
    '''Creates template .cfg files for Atari THE400 Mini.'''
    # Build the configuration file.
    configuration = build_config(model, basic, video_std, force_pal, artefact,
       start, height, width)
    
    # Write the configuration file to the specified file, or stdout.
    for line in configuration:
        filename.write(line + '\n')
    
    filename.close()
    exit(SUCCESS)    

@config.command()
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
    default='1', show_default=True, help='Status/progress reporting verbosity')
def apply(verbosity: str):
    '''Applies specified .cfg template to THE400 Mini USB Media games.'''
    pass

# Configuration File Functions
def build_config(model: str, basic: bool, video_std: str, force_pal: bool,
        artefact: str, start: int, height: int, width:int) -> list:
    entries = []
    add_emulator_settings(entries, model, basic, video_std, force_pal, artefact)
    add_input_analog_settings(entries)    
    add_display_settings(entries, start, height, width)
    add_controller_mappings(entries, model)
    return entries

def add_emulator_settings(config: list, model: str, basic: bool, video_std: str,
    force_pal: bool, artefact: str):
    '''Adds emulator settings to the configuration file.'''
    # Build the main machine/model/basic entry
    model_value = MODEL_MACHINE_ID[model]
    basic_value = f'{EMULATOR_SEPARATOR}{BASIC}' if basic else ''
    machine = (f'{KEY_EMULATOR_PREFIX}{KEY_EMULATOR_MACHINE}'
               f' = "{model_value}{basic_value}'
               f'{EMULATOR_SEPARATOR}{video_std.lower()}"{EOL}')
    config.append(machine)

    # Add artefact and force_pal settings
    config.append(f'{KEY_EMULATOR_PREFIX}{KEY_EMULATOR_ARTEFACT}'
                    f' = {artefact}{EOL}')
    config.append(f'{KEY_EMULATOR_PREFIX}{KEY_EMULATOR_FORCE_PAL}'
                    f' = {str(force_pal).lower()}{EOL}')

def add_input_analog_settings(config: list):
    '''Adds default input_analogue settings to the configuration file.'''
    config.append(f'{KEY_INPUT_ANALOG_PREFIX}{KEY_ANALOG_RATE}'
                  f' = {DEFAULT_ANALOG_RATE}{EOL}')
    config.append(f'{KEY_INPUT_ANALOG_PREFIX}{KEY_ANALOG_CURVE}'
                  f' = "{DEFAULT_ANALOG_CURVE}"{EOL}')
    config.append(f'{KEY_INPUT_ANALOG_PREFIX}{KEY_ANALOG_AUTO_CENTER}'
                  f' = "{DEFAULT_AUTO_CENTER}"{EOL}')

def add_display_settings(config: list, start: int, height: int, width: int):
    '''Adds default display settings to the configuration file.'''
    config.append(f'{KEY_DISPLAY_PREFIX}{KEY_DISPLAY_START}'
                  f' = {start}{EOL}')
    config.append(f'{KEY_DISPLAY_PREFIX}{KEY_DISPLAY_HEIGHT}'
                  f' = {height}{EOL}')
    config.append(f'{KEY_DISPLAY_PREFIX}{KEY_DISPLAY_WIDTH}'
                  f' = {width}{EOL}')
    
def add_controller_mappings(config: list, model: str):
    '''Adds default controller mapping to the configuration file.'''
    # Select the correct set of controller values
    controller_values = (
        CONTROLLER_DEFAULTS if model != '5200' else CONTROLLER_5200_DEFAULTS)
    
    # Add default controller settings
    for controller in range(NUMBER_OF_CONTROLLERS):
        for key in controller_values:
            line = (f'{CONTROLLER_PREIX}{controller}{CONTROLLER_SEPARATOR}{key}'
                    f' = "{controller_values[key]}"{EOL}')
            config.append(line)

    return config

# Run!
if __name__ == '__main__':
    config()