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

# Default Argument Values
DEFAULT_MAX_FILES_PER_FOLDER = 250
DEFAULT_MIN_FILES_PER_FOLDER = 1
DEFAULT_PRESERVE_GROUPING = True

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
	help='Groups files by like prefixes',
	show_default=True)
@click.option('-m', '--max', type=int, default=DEFAULT_MAX_FILES_PER_FOLDER,
	show_default=True, help='Maximum # of files per partition')
@click.option('-v', '--verbosity', type=click.Choice(['0', '1', '2']),
	default='1', show_default=True, help='Status/progress reporting verbosity')
@click.argument('source_path', default='./',
	type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('dest_path', default='./',
	type=click.Path(exists=False, file_okay=False, dir_okay=True))
def partition(copy: bool, delete: bool,	group: bool, max: int,
	verbosity: str,	source_path: str, dest_path: str) -> int:
	'''Splits a set of source files into smaller, alphabetic, partitions.'''

	# Sanity check input
	if source_path == dest_path:
		click.echo(
			f'{ERROR_TEXT}SOURCE_PATH: "{source_path}" and DEST_PATH: '
			f'"{dest_path}" cannot be the same.', err=True)
		exit(ERROR)

	if max < DEFAULT_MIN_FILES_PER_FOLDER:
		click.echo(
			f'{ERROR_TEXT}Maximum number of filers per parition must be '
			f'at least {DEFAULT_MIN_FILES_PER_FOLDER}.', err=True)
		exit(ERROR)

	pass

# Run!
if __name__ == '__main__':
    aemt()