#!python3

# atr.py - Atari 8-bit ATR Disk Image Utility & Functions
#
# Copyright(C) 2026, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
import pathlib

# 3rd Party/External Modules
import click

# Constants

# Error Messages and Command Result Exit Codes
ERROR_TEXT ='Error: '
ERROR = 1
SUCCESS = 0

# Status Messages
PROTECT_SUCCESS = 'Write-protected.'
UNPROTECT_SUCCESS = 'Write-protection disabled.'

# .ATR File Constants
ATR_PATTERN = '*.atr'
ATR_PATTERN_RECR = '**/*.atr'
STATUS_BYTE_INDEX = 0x0F
PROTECT_BIT_MASK = 0x01
UNPROTECT_BIT_MASK = 0xFE

@click.group()
@click.version_option('0.0.1.1')
def atr():
    '''Manipulates Atari 8-bit .ATR disk images.'''
    pass

@atr.command('protect')
@click.option('-r', '--recurse', is_flag=True, default=False,
    help='Process directories recursively for .atr files')
@click.option('-v', '--verbose', is_flag=True, default=False,
    help='Verbose output')
@click.argument('source_path', 
    type=click.Path(exists=True, file_okay=True, dir_okay=True))
def protect(recurse: bool, verbose: bool, source_path: str):
    '''Write-Protect .ATR disk images by setting the write-protect bit
    in the header.      
    
    SOURCE_PATH may be a directory or a file; if a directory *only* .atr files
    will be processed.  The -r/--recurse option will include subdirectories.
    '''
    ret_val = process_atr_files(source_path, recurse, verbose, protect=True)
    exit(ret_val)

@atr.command('unprotect')
@click.option('-r', '--recurse', is_flag=True, default=False,
    help='Process directories recursively for .atr files')
@click.option('-v', '--verbose', is_flag=True, default=False,
    help='Verbose output')
@click.argument('source_path', 
    type=click.Path(exists=True, file_okay=True, dir_okay=True))
def unprotect(recurse: bool, verbose: bool, source_path: str):
    '''Remove write-protection from .ATR disk images by clearing the
    write-protect bit in the header.         
    
    SOURCE_PATH may be a directory or a file; if a directory *only* .atr files
    will be processed.  The -r/--recurse option will include subdirectories.
    '''
    ret_val = process_atr_files(source_path, recurse, verbose, protect=False)
    exit(ret_val)

@atr.command('status')
@click.option('-r', '--recurse', is_flag=True, default=False,
    help='Process directories recursively for .atr files')
@click.argument('source_path', 
    type=click.Path(exists=True, file_okay=True, dir_okay=True))
def status(recurse: bool, source_path: str):
    '''Display the write-protection status of .ATR disk images.
    
    SOURCE_PATH may be a directory or a file; if a directory *only* .atr files
    will be processed.  The -r/--recurse option will include subdirectories.
    '''
    files = build_source_file_list(source_path, recurse)

    if not files:
        click.echo(ERROR_TEXT + 'No .atr files found to process.')
        exit(ERROR)
    
    for file in files:
        is_protected = get_file_protection_status(file)
        status_text = PROTECT_SUCCESS if is_protected else UNPROTECT_SUCCESS
        click.echo(f'{file}: {status_text}')
        exit(SUCCESS)

def build_source_file_list(source_path: str, recurse: bool) -> list:
    # We can work on a single file, or a directory (with optional recursion),
    # so build a list of file(s) accordingly
    source_path = pathlib.Path(source_path)
    files = None
    if source_path.is_file():
        files = []
        files.append(source_path)
    elif source_path.is_dir():
        pattern = ATR_PATTERN_RECR if recurse else ATR_PATTERN      
        files = list(source_path.glob(pattern))
        files.sort(key=lambda x: x.name.lower())
            
    return files

def process_atr_files(
    source_path: str, recurse: bool, verbose: bool, protect: bool) -> int:

    files = build_source_file_list(source_path, recurse)
    if not files:
        click.echo(ERROR_TEXT + 'No .atr files found to process.')
        return ERROR

    for file in files:
        set_file_protection(file, protect)

        if verbose:
            action = PROTECT_SUCCESS if protect else UNPROTECT_SUCCESS
            click.echo(f'{file}: {action}')

    return SUCCESS

def get_file_protection_status(file: pathlib.Path) -> bool:
    with open(file, 'rb') as atr_file:
        # Read the status byte from the header
        atr_file.seek(STATUS_BYTE_INDEX)
        status_byte = atr_file.read(1)[0]
        atr_file.close()             

    return (status_byte & PROTECT_BIT_MASK) != 0

def set_file_protection(file: pathlib.Path, protect: bool) -> int:
    with open(file, 'rb+' ) as atr_file:
        # Read the status byte from the header
        atr_file.seek(STATUS_BYTE_INDEX)
        status_byte = atr_file.read(1)[0]

        # Modify the status byte to set or clear the write-protect bit
        new_status_byte = set_protect_bit(bytes([status_byte]), protect)[0]
       
        # Write the modified status byte back to the header
        atr_file.seek(STATUS_BYTE_INDEX)
        atr_file.write(bytes([new_status_byte]))

        atr_file.flush()
        atr_file.close()

    return SUCCESS

def set_protect_bit(status_byte: bytes, protect: bool) -> bytes:
    if protect:
        return bytes([status_byte[0] | PROTECT_BIT_MASK])
    else:
        return bytes([status_byte[0] & UNPROTECT_BIT_MASK])    

# Run!
if __name__ == '__main__':
    atr()