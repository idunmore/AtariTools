# config.py - Atari THE400 Mini Configuration Utility & Functions
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
import pathlib
import shutil

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

# File Constants
TARGET_PATTERN = '*.*'
TARGET_PATTERN_RECR = '**/*'

# Suffix and Extension NEED to be different due to the way pathlib works;
# path.with_suffix() replaces the last suffix with the new one, where
# path.suffix does NOT return the separating period.
CFG_SUFFIX = '.cfg'
CFG_EXTENSION = 'cfg'

# THE400 Mini CONFIG Constants

EOL = ';'
KEY_VALUE_SEPARATOR = '='

# Atari Media File Extensions
MEDIA_EXTENSIONS = ['atr', 'atx', 'xfd', 'dcm', 'com', 'exe', 'xex', 'cas',
                    'car', 'crt', 'rom', 'bin', 'a52', 'm3u']
FIRST_CARTRIDGE_TYPE = 1
LAST_CARTRIDGE_TYPE = 70

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
@click.version_option('0.1.0.0')
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
    '''Creates .cfg files for Atari THE400 Mini.'''
    # Build the configuration file.
    configuration = build_config(model, basic, video_std, force_pal, artefact,
       start, height, width)
    
    # Write the configuration file to the specified file, or stdout.
    for line in configuration:
        filename.write(line + '\n')
    
    filename.close()
    exit(SUCCESS)    

@config.command()
@click.option('-o', '--overwrite', is_flag=True, default=False,
        help='Overwrite existing .cfg files')
@click.option('-r', '--recurse', is_flag=True, default=False,
    help='Recursively process all files in target directory')
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
    default='1', show_default=True, help='Status/progress reporting verbosity')
@click.argument('config_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('dest_path', type=click.Path(exists=True, dir_okay=True))
def apply(overwrite: bool, recurse: bool, verbosity: str,
          config_file: str, dest_path: str):
    '''Applies specified .cfg file to THE400 Mini USB Media games.'''
    extensions = get_extensions()
    target_files = build_target_file_list(pathlib.Path(dest_path), extensions,
                                          recurse)

    if int(verbosity) == PROGRESS:
        # ... showing a progress bar.
        with click.progressbar(target_files, label='Applying config') as bar:
            for file in bar:
                apply_config(config_file, file, overwrite, verbosity)        
    else:
        for file in target_files:
            apply_config(config_file, file, overwrite, verbosity)           
 
    exit(SUCCESS)

@config.command()
@click.option('-r', '--recurse', is_flag=True, default=False,
    help='Recursively process all files in target directory')
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
    default='1', show_default=True, help='Status/progress reporting verbosity')
@click.argument('update_file', type=click.Path(exists=True, dir_okay=False))
@click.argument('dest_path', type=click.Path(exists=True, dir_okay=True))
def update(recurse: bool, verbosity: str, update_file: str, dest_path: str):
    '''Updates .cfg files with settings from specified update file.'''
    # Load the update file, ONCE:
    update_file_data = load_config_data(pathlib.Path(update_file))

    # Our target files are all files with the .cfg extension    
    extensions = [CFG_EXTENSION]
    target_files = build_target_file_list(pathlib.Path(dest_path), extensions,
                                          recurse)
    
    if int(verbosity) == PROGRESS:
        # ... showing a progress bar.
        with click.progressbar(target_files, label='Updating config') as bar:
            for target_file in bar:
                update_config_file(update_file_data, target_file)        
    else:
        for target_file in target_files:
            update_config_file(update_file_data, target_file)
            echo_v(f'Updated: {target_file} with: {update_file}',
                   int(verbosity))      

    exit(SUCCESS)

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

def update_config(config_updates: list, target_config: list):
    '''Updates the specified configuration file with the new settings.'''
    # Iterate through the new configuration settings   
    for update_item in config_updates:
        item_found = False
        update_key = get_config_item_key(update_item)
        for target_item in target_config:
            # Update the existing config item if it exists ...
            if update_key == get_config_item_key(target_item):               
                target_config[target_config.index(target_item)] = update_item              
                item_found = True
                break           
        
        if not item_found:
            # ... otherwise add the new config item.            
            target_config.append(update_item)  
            
def get_config_item_key(config_item: str) -> str:
    '''Extracts the key from a configuration line item.'''
    return config_item.split(KEY_VALUE_SEPARATOR)[0].strip()

def get_extensions() -> list:
    '''Returns the list of supported Atari media file extensions.'''
    # Start with the default list of extensions ...
    extensions = MEDIA_EXTENSIONS
    # ... and add all the specific cartridge extensions:
    for number in range(FIRST_CARTRIDGE_TYPE, LAST_CARTRIDGE_TYPE + 1):
        extensions.append(f'c{number:02d}')

    return extensions

def build_target_file_list(dest_path: pathlib.Path, extensions: list,
                           recurse: bool = False) -> list:
    # Anything files with extensions not in this list are excluded    
    target_files = []
    # Single file?
    if dest_path.is_file() and dest_path.suffix[1:].lower() in extensions:
        # Add file, replacing the extension with '.cfg'
        target_files.append(dest_path.with_suffix(CFG_SUFFIX))
    
    # Directory?
    if dest_path.is_dir():
        # Recurse if specied ...
        pattern = TARGET_PATTERN_RECR if recurse else TARGET_PATTERN  
        # ... and find all files ...      
        candidate_files = list(dest_path.glob(pattern))  
        # ... adding only those with valid extensions, but replacing the
        # extension with '.cfg'      
        target_files = [file.with_suffix(CFG_SUFFIX)
                        for file in candidate_files
                        if (file.is_file() and
                            file.suffix[1:].lower() in extensions)]
    
    return target_files

def apply_config(config_file: str, target_file: pathlib.Path, overwrite: bool,
                 verbosity: str):
    '''Applies the specified configuration file to the target file.'''
    if not target_file.exists() or overwrite:
        shutil.copy(config_file, target_file)
        echo_v(f'Applied {pathlib.Path(config_file)} to: {target_file}',
                int(verbosity))

def load_config_data(update_file: pathlib.Path) -> list:
    '''Loads the specified update file into a list of configuration items.'''    
    with open(update_file, 'r') as file:
        lines = [line.rstrip() for line in file]
    return lines

def update_config_file(update_file: list, target_file: pathlib.Path):
    '''Updates the specified configuration file with the new settings.'''
    target_config = load_config_data(target_file)
    # Update the target file with the new settings
    update_config(update_file, target_config)
    # Write the updated target file
    with open(target_file, 'w') as file:
        for line in target_config:
            file.write(line + '\n')

# GENERAL Utility Functions

def echo_v(message: str, verbosity: int):
    if verbosity == VERBOSE:
        click.echo(message)	

# Run!
if __name__ == '__main__':
    config()