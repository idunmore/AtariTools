# AEMT.py - [A]tari [E]ight-bit [M]ulti-[T]ool
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules
import pathlib
import os.path
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

# Default Argument Values
DEFAULT_MAX_FILES_PER_FOLDER = 250
DEFAULT_MIN_FILES_PER_FOLDER = 1
DEFAULT_PRESERVE_GROUPING = False

# File and Path Patterns
SOURCE_FILE_PATTERN = "**/*.exe"

# Command Line Interface

@click.group()
@click.version_option('0.0.0.1')
def aemt():
	'''[A]tari [E]ight-bit [M]ulti-[T]ool

			Moves files to organized folder structures, with an optionally
			limited	number of files per folder.

			Fingerprints game images, identifies image file types and creates
			.cfg files for Atari THE400 Mini games on USB media.'''
	pass

@aemt.command('partition')
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
def partition_command(copy: bool, delete: bool,	group: bool, max_files: int,
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

	partition(copy, delete, group, max_files, int(verbosity),
		source_path, dest_path)

	pass

# PARTITION Classes and Functions
def partition(copy: bool, delete:bool, group: bool, max_files: int,
	verbosity: int,	source_path: str, dest_path: str) -> int:

	file_list = build_source_file_list(source_path)
	if file_list == None or len(file_list) < 1:
		echo_v('No files to partition.', verbosity)
		return SUCCESS

	grouper = MaxFilesPerFolder(file_list, max_files, group)
	file_groups = grouper.filegroups
	if file_groups == None or len(file_groups) < 1:
		echo_v('No files groups to partition.', verbosity)
		return SUCCESS	

	return 0


def build_source_file_list(source_path: str) -> list:
	'''Builds the raw list of source files to be partitioned.'''
	source_path = pathlib.Path(source_path)
	source_files = list(source_path.glob(SOURCE_FILE_PATTERN))
	# Sort the files, by name, as they will be grouped alphaetically.
	source_files.sort(key=lambda x : x.name.lower())
	return source_files 

# A FileGroup is a LIST of SOURCE PATHS (with filenames) for all of the files
# the group contains.  A FileGroup contains files intended for a single, common
# destination folder/group.
class FileGroup(list):	

	@property
	def common_prefix(self: Self) -> str:
		# The common prefix of the file name, NOT the whole path.  Outputs are
		# based on the file's name, not what folder it came from.
		filenames = [path.name.lower() for path in self]
		return os.path.commonprefix(filenames)

	@property
	def common_prefix_length(self: Self) -> int:
		return len(self.common_prefix)

	@property
	def first_prefix(self: Self) -> str:
		# The first UNIQUE prefix is the COMMON prefix plus the next character.
		return self[0].name[0:self.common_prefix_length + 1]
	
	@property
	def last_prefix(self: Self) -> str:
		# The last UNIQUE prefix is the COMMON prefix plus the next character.
		return self[len(self) - 1].name[0:self.common_prefix_length + 1]

	def get_n_first_prefix_chars(self: Self, length: int) -> str:
		return self[0].name[0:length]

	def get_n_last_prefix_chars(self: Self, length: int) -> str:
		return self[len(self) - 1].name[0:length]
		
# FileGroups are a list of individual FileGroup objects, and represent the
# entire set of files to be processed.
class FileGroups(list):
	
	def get_folder_range(self: Self, filegroup: FileGroup) -> (str, str):
		# Find the PRIOR FileGroup
		index = self.index(filegroup)
		prior_filegroup = self[index - 1] if index > 0 else None

		start_prefix_length = filegroup.common_prefix_length + 1
		end_prefix_length = start_prefix_length
		if prior_filegroup != None:
			# If the FIRST character of the LAST file in the PRIOR GROUP is the
			# same as the FIRST character of the LAST file in the CURRENT GROUP,
			# then we need to qualify the start of the range with an
			# extra character.
			if (prior_filegroup.get_n_last_prefix_chars(start_prefix_length) ==
				filegroup.get_n_first_prefix_chars(start_prefix_length)):
				start_prefix_length += 1
			else:
				# Otherwise, shorten the FIRST folder name as long as that
				# maintains a unique range (first and last folder names
				# are unique in the first character).  This avoids
				# "SA-SF", and instead gives "S-SF", "SG-SM" etc.
				if start_prefix_length > 1:
					if (prior_filegroup.get_n_last_prefix_chars(1) !=
						filegroup.get_n_first_prefix_chars(1)):
						 start_prefix_length -= 1

		# If there is a NEXT filegroup ...
		if len(self) > index + 1:
			next_filegroup = self[index + 1]
			# ... we may need to shorten the END prefix, if it starts a whole
			# new letter, and is shorter than the START prefix ...			
			if (filegroup.get_n_last_prefix_chars(1) !=
				next_filegroup.get_n_first_prefix_chars(1)):
					if end_prefix_length < start_prefix_length:
						# Can't be less then ONE character
						if end_prefix_length > 1: end_prefix_length -= 1			


		return (filegroup[0].name[0:start_prefix_length],
				filegroup[len(filegroup) - 1].name[0:end_prefix_length] )

class MaxFilesPerFolder(list):

	def __init__(
			self: Self,
			path_list: list,
			max_files_per_folder: int = DEFAULT_MAX_FILES_PER_FOLDER,
			preserve_grouping: bool = DEFAULT_PRESERVE_GROUPING
		):
		# Initialize our underlying LIST
		list.__init__(self, path_list)

		# Handle additional arguments.
		if max_files_per_folder < DEFAULT_MIN_FILES_PER_FOLDER:
			raise ValueError(
				f'Maximum number of filers per folder cannot be less than '
				f'{DEFAULT_MIN_FILES_PER_FOLDER}.')

		self._max_files_per_folder = max_files_per_folder
		self._preserve_grouping = preserve_grouping

	def _adjust_group(self, group, current_file) -> int:
		# Adjust this group so we don't split file prefixes across groups.
		
		# To do this, we need to compare the extend prefix (the common prefix
		# plus one additional character) of THIS group's LAST file name, to that
		# of the FIRST file in the NEXT group.		
		prefix_length = group.common_prefix_length + 1
		last_prefix = self[current_file - 1].name[0:prefix_length]
		current_prefix = self[current_file].name[0:prefix_length]
		
		# IF our prefixes are the same, we DO have prefixes spanning groups.
		# To fix this, we remove the last entries from THIS group and reset our
		# file pointer so the trimmed files can ALL go in the NEXT group.
		if last_prefix == current_prefix:
			# Start on PREVIOUS file, so it gets included in the right group.
			current_file -= 1			
			while(current_file > 0):				
				if self[current_file].name[0:prefix_length] == last_prefix:					
					group.pop()
					current_file -= 1
				else:
					break
			# Don't include the last file in both batches!
			current_file += 1

		return current_file

	@property
	def filegroups(self: Self) -> FileGroups:		
		
		total_file_count = len(self)
		current_file = 0
		group_file_count = 0
		group = FileGroup()
		groups = FileGroups()
		groups.append(group)		

		# Process ALL files ...
		while(current_file < total_file_count):
			if group_file_count < self._max_files_per_folder:
				# Add FILES to this GROUP as long as we've not hit our maximum
				group.append(self[current_file])
				current_file += 1
				group_file_count += 1
			else:
				# We've hit the maximum number of files for this group; do
				# we need to adjust the group to preserve file grouping?
				if self._preserve_grouping == True:
					current_file = self._adjust_group(group, current_file)

				# Starts a new group of files.
				group = FileGroup()
				groups.append(group)
				group_file_count = 0

		return groups		

# GENERAL Utility Functions
def echo_v(message: str, verbosity: int):
	if verbosity == VERBOSE:
		click.echo(message)	

# Run!
if __name__ == '__main__':
    aemt()