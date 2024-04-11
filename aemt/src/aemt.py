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




@click.group()
@click.version_option('0.0.0.1')
def aemt():
	'''[A]tari [E]ight-bit [M]ulti-[T]ool

			Moves files to organized folder structures, with an optionally
			limited	number of files per folder.

			Fingerprints game images, identifies image file types and creates
			.cfg files for Atari THE400 Mini games on USB media.'''
	pass

# Run!
if __name__ == '__main__':
    aemt()