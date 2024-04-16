# AEMT.py - [A]tari [E]ight-bit [M]ulti-[T]ool
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
import itertools
import pathlib
import os.path
import string
from typing import Self, Iterator

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

# Default Argument Values
DEFAULT_MAX_FILES_PER_FOLDER = 250
DEFAULT_MIN_FILES_PER_FOLDER = 1
DEFAULT_PRESERVE_GROUPING = False

# File and Path Patterns
SOURCE_FILE_PATTERN = '**/[!.]*.*'
NUMERIC_FOLDER_NAME = '0-9'

BAND_SEPARATOR = '-'
FOLDER_RANGE_SEPARATOR = '->'

# File and Folder Structures
class Folder(list):
    '''A list of files, representing a single folder.'''
    def __init__(self: Self, name: str = ''):
        super().__init__()
        self._name = name

    @property
    def name(self: Self) -> str:
        return self._name
    
    @name.setter
    def name(self: Self, name: str):
        self._name = name

    @property
    def first_filename(self: Self) -> str:
        '''Returns the name of the first file in the folder.'''
        return '' if len(self) == 0 else self[0].name 

    @property
    def last_filename(self: Self) -> str:
        '''Returns the name of the last file in the folder.'''
        return '' if len(self) == 0 else self[len(self) - 1].name
    
    @property
    def common_prefix(self: Self) -> str:
        '''Returns the common prefix of all files in the folder.'''
        return os.path.commonprefix([file.name for file in self])
    
class Folders(list):
    '''A list of folders, representing the entire file structure.'''
    def __init__(self: Self):
        super().__init__()      
    
# Splitters

class Splitter:
    '''Base class for all file splitters.'''
    def __init__(self: Self, files: list):
        self._files = files
        files.sort(key=lambda x : x.name.lower())

    def split(self: Self) -> Folders:
        '''Splits the files into folders.'''
        return Folders()

    @property
    def folders(self: Self):
        return None
    
class SimpleSplit(Splitter):
    '''Splits files individual folders, based on the file's first character.'''
    def __init__(self: Self, files: list):
        super().__init__(files)

    def split(self: Self) -> Folders:
        '''Splits the files into folders, one per unique first character.'''
        key_func = lambda x: x.name[0].lower()
        folder_dict = {key: list(group) for key, group
            in itertools.groupby(self._files, key_func)}
        
        # Create the Folders container, to add individual folders to.
        folders = Folders()

        self._add_numeric_folder(folder_dict, folders)
        self._add_alpha_folders(folder_dict, folders)

        return folders     
    
    def _add_numeric_folder(self: Self, folder_dict: dict, folders: Folders):
        # Group all the numeric prefixes into one folder.
        folder = Folder(NUMERIC_FOLDER_NAME)        
        
        for key in folder_dict.keys():
            if key in string.digits:
                for file in folder_dict[key]:
                    folder.append(file)
        folders.append(folder)

    def _add_alpha_folders(self:Self, folder_dict: dict, folders: Folders):
        '''Add all non-numeric folders to the Folders container.'''
        for key in folder_dict.keys():
            if key in string.ascii_lowercase:
                folder = Folder(key)
                for file in folder_dict[key]:
                    folder.append(file)
                folders.append(folder)
    
    @property
    def folders(self: Self):
        return None

class BandSplit(Splitter):
    '''Splits files folders, based on groups of the file's first character.'''
    def __init__(self: Self, files: list):
        super().__init__(files)

    def split(self: Self, bands: list) -> Folders:
        
        key_func = lambda x: x.name[0].lower()
        folder_dict = {key: list(group) for key, group
            in itertools.groupby(self._files, key_func)}
        
        folders = Folders()
        self._add_folder_bands(folder_dict, folders, bands)

        return folders
    
    def _add_folder_bands(
        self: Self, folder_dict: dict, folders: Folders, bands: list):
            # Go one band at a time ...
            for band in bands:
                start, end = self._get_band_extents(band.lower())
                # ... creating a new folder for each band ...
                folder = Folder(band.upper())
                # ... then for every character prefix in the band ...
                for char in char_range(start, end):
                    # ... find the matching folders in the overall list ...                   
                    for key in folder_dict.keys():
                        if key[0] == char:
                            # ... and all all of its files to the folder.
                            for file in folder_dict[key]:
                                folder.append(file)
                # Add this folder, which contains all files for this band
                # to the overall list of folders.
                folders.append(folder)                
                
    def _get_band_extents(self: Self, band: str) -> tuple[str, str]:
        '''Returns the first and last characters (range) of a band.'''
        extents = band.split(BAND_SEPARATOR)
        if len(extents) != 2:
            raise ValueError(
                f'{ERROR_TEXT}Invalid band: "{band}" - '
                f'expected format is "A-E", "A-Z", or "0-9"')
        
        start = extents[0]
        end = extents[1]        
        if start >= end:
            raise ValueError(
                f'{ERROR_TEXT}Invalid band: "{band}" - '
                f'end ({end}) must be greater than start ({start})')
        
        return (start, end)

class MaxFileSplit(Splitter):
    '''Splits files individual folders, based on the file's first character.'''
    def __init__(self: Self, files: list):
        super().__init__(files)

    def split(self: Self, max_files_per_folder: int, group: bool) -> Folders:
        '''Splits the files into folders, with a maximum number of files per
        folder.  Optionally, tries to keep files with like-prefixes together,
        which may result in fewer files per folder.'''
        total_files = len(self._files)
        current_file = 0
        folder_file_count = 0
        folders = Folders()
        folder = Folder()
        folders.append(folder)

        # Process all files ... one at a time, in order ...
        while(current_file < total_files):
            # ... if there's still room in the folder, add the current file ...
            if folder_file_count < max_files_per_folder:
                folder.append(self._files[current_file])
                folder_file_count += 1
                current_file += 1
            else:
                # Folder is full, so we need another; first adjust the current
                # folder (which may remove files) to group like-prefixes.
                if group:
                    current_file = self._adjust_folder(folder, current_file)
                
                # Now we can start a new folder.
                folder = Folder()
                folders.append(folder)
                folder_file_count = 0

        self._set_folder_names(folders)
        return folders

    def _adjust_folder(self: Self, folder: Folder, current_file: int) -> int:
        # Adjust folder content to keep like-prefixes together as much as
        # possible.  For example, don't split 'AA*' files into two folders;
        # instead stop at 'AAA*' and start a new folder for # 'AAB*' files.
        prefix_length = len(folder.common_prefix) + 1
        last_prefix = self._files[current_file - 1].name[:prefix_length]
        current_prefix = self._files[current_file].name[:prefix_length]

        # Nothing to do unless the prefixes of the first and last files in the
        # folder have the same prefix.
        if last_prefix == current_prefix:
            # Starting with the PREVIOUS file ...
            current_file -= 1
            while(current_file > 0):
                # ... remove files from the folder until prefixes don't match.
                if (self._files[current_file].name[:prefix_length] ==
                    last_prefix ):
                    folder.pop()
                    current_file -= 1
                else:
                    break

            # Don't add the LAST file to both folders!
            current_file += 1

        return current_file

    def _set_folder_names(self: Self, folders: Folders):
        '''Sets the names of the folders based on their contents.'''
        # Setup the start of the name for the first folder ...           
        self._set_first_folder_name_start(folders)    
        # We do the start of all ours folder's name/ranges first ...
        self._set_folder_name_start(folders)     
        # ... as the end name is dependent on the start name/range.   
        self._set_folder_name_end(folders)    
         # Unique processing for the LAST folder.        
        self._set_last_folder_name_end(folders)       

    def _set_first_folder_name_start(self: Self, folders: Folders):
        '''Sets the start of the first folder's name.'''
        # The FIRST folder's start prefix is ALWAYS just the first character
        # of its FIRST file name.            
        folders[0].name = folders[0].first_filename[0]

    def _set_folder_name_start(self: Self, folders: Folders):
        '''Sets the start name range for each folder.'''
        # We've already done the first folder, so continue from the second.
        current_folder_index = 1
        
        # We are just doing the START name for each folder.       
        num_folders = len(folders)
        while(current_folder_index < num_folders):
            last_folder = folders[current_folder_index - 1]
            current_folder = folders[current_folder_index]

            # The start of the folder name is the name of its first filename
            # UPTO the point that it first differs from its last filename.
            start_length = first_different_character_index(
                current_folder.first_filename,
                last_folder.last_filename)            
            start = current_folder.first_filename[:start_length + 1]
            current_folder.name = f'{start}'

            current_folder_index += 1

    def _set_folder_name_end(self: Self, folders: Folders):        
        num_folders = len(folders)           
        current_folder_index = 0
        # Do all folders, except the last one - which get special handling.
        while(current_folder_index < num_folders - 1):
            current_folder = folders[current_folder_index]
            next_folder = folders[current_folder_index + 1]            

            # The simple end of the folder name is name of its last filename
            # UPTO the point that it first differs from the next folder's
            # first filename.                  
            end_length = first_different_character_index(
                current_folder.last_filename,
                next_folder.first_filename)
            
            # If the current (start) name of the folder is longer than the end
            # AND it is s different character, then we can shorted end by one
            # character so we're not overqualifying the end name.
            if (len(current_folder.name) > end_length and
                current_folder.first_filename[0] ==
                current_folder.last_filename[0]):
                    end_length = len(current_folder.name) - 1        

            end = current_folder.last_filename[:end_length + 1]

            # Add end to the folder name ONLY if it is different to start (name)
            if current_folder.name != end:
                current_folder.name += f'{FOLDER_RANGE_SEPARATOR}{end}'
            
            current_folder_index += 1       

    def _set_last_folder_name_end(self: Self, folders: Folders):
        '''Sets the end prefix of the last folder.'''
        # Get the last folder in the Folders collection.
        last_folder = folders[len(folders) - 1]
        start = last_folder.name
          
        if start[0] == last_folder.last_filename[0]:
            # The last file in the folder has the same prefix as the first, so
            # we need to make the end as long as the start.
            end = last_folder.last_filename[0:len(start)]
        else:
            # The last file in the folder has a different prefix than the
            # first, so we only need the first letter of the last file's name
            # (as there can be no more files/divisions).
            end = last_folder.last_filename[0]

        # If the start and end range of the folder is the same, then we don't
        # need to show the end.        
        if start == end: end = ''
        
        last_folder.name = f'{start}{FOLDER_RANGE_SEPARATOR}{end}'    

# Command Line Interface

@click.group()
@click.version_option('0.0.0.2')
def aemt():
    '''[A]tari [E]ight-bit [M]ulti-[T]ool

            Moves files to organized folder structures, with an optionally
            limited	number of files per folder.

            Fingerprints game images, identifies image file types and creates
            .cfg files for Atari THE400 Mini games on USB media.'''
    pass

@aemt.command('split')
@click.option('-c', '--copy', is_flag=True, default=False,
    help= f'Copies files to new partitions (else does nothing)')
@click.option('-d', '--delete', is_flag=True, default=False,
    help= 'Deletes original files after copying them (move)')
@click.option('-g', '--group', is_flag=True, default=DEFAULT_PRESERVE_GROUPING,
    help='Groups files by like prefixes')
@click.option('-m', '--max_files', type=int, default=DEFAULT_MAX_FILES_PER_FOLDER,
    show_default=True, help='Maximum # of files per partition')
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
    default='1', show_default=True, help='Status/progress reporting verbosity')
@click.argument('source_path', default='./',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('dest_path', default='./',
    type=click.Path(exists=False, file_okay=False, dir_okay=True))
def split_command(copy: bool, delete: bool,	group: bool, max_files: int,
    verbosity: str,	source_path: str, dest_path: str) -> int:
    '''Splits a set of source files into smaller, alphabetic, partitions.'''

    # Sanity check input
    if source_path == dest_path:
        click.echo(
            f'{ERROR_TEXT}SOURCE_PATH: "{source_path}" and DEST_PATH: '
            f'"{dest_path}" cannot be the same.', err=True)
        exit(ERROR)

    if max_files < DEFAULT_MIN_FILES_PER_FOLDER:
        click.echo(
            f'{ERROR_TEXT}Maximum number of filers per parition must be '
            f'at least {DEFAULT_MIN_FILES_PER_FOLDER}.', err=True)
        exit(ERROR)    

    #test_split_simple(source_path)
    #test_band_split(source_path)
    max_files_split(source_path)
    print("\nDONE!")

# Test(er) Functions

def test_split_simple(source_path: str):
    file_list = build_source_file_list(source_path)
    splitter = SimpleSplit(file_list)
    folders = splitter.split()

    print_folders(folders)

def test_band_split(source_path: str):
    file_list = build_source_file_list(source_path)
    splitter = BandSplit(file_list)
    folders = splitter.split(['0-9','a-e','f-j','k-o','p-t','u-z'])

    print_folders(folders)

def max_files_split(source_path: str):
    file_list = build_source_file_list(source_path)
    splitter = MaxFileSplit(file_list)
    folders = splitter.split(250, False)

    print_folders(folders)
    
def print_folders(folders: Folders):
    for folder in folders:
        print(f'\n{folder.name} : {len(folder)}')
        
        for file in folder:
            print(f'  {file.name}')

# GENERAL Utility Functions

def build_source_file_list(source_path: str) -> list:
    '''Builds the raw list of source files to be partitioned.'''
    source_path = pathlib.Path(source_path)
    source_files = list(source_path.glob(SOURCE_FILE_PATTERN))
    # Sort the files, by name, as they will be grouped alphaetically.
    source_files.sort(key=lambda x : x.name)
    return source_files 

def char_range(start: str, end: str) -> Iterator[str]:
    '''Generates the characters from start to end, inclusive.'''
    for c in range(ord(start), ord(end) + 1):
        yield chr(c)

def first_different_character_index(first: str, second: str) -> int:
    '''Gets index of first character that differs between two strings.'''
    for index, (char1, char2) in enumerate(zip(first, second)):
        if char1 != char2:
            return index
    return -1

def echo_v(message: str, verbosity: int):
    if verbosity == VERBOSE:
        click.echo(message)	

# Run!
if __name__ == '__main__':
    aemt()