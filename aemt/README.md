# [A]tari [E]ight-bit [M]ulti-[T]ool - aemt.py

This is a command-line tool, intended to provide some "quality of life" improvements to managing large game/program libraries, on USB Media, for the "Atari THE400 Mini" (with utilities for other Atari 8-bit emulators).

Current functionality includes:

* Moving files, in bulk, to organized folder structures - with the ability
  to control how the organization is done and to limit the number of files
  per folder (to avoid exceeding "THE400 Minis" 255 files-per-folder limit).

* Creating, applying, and updating .cfg files automatically, WITHOUT having
  to set them individually, one game at a time, from within "THE400 Mini's"
  file browser.

* Identify and validate CARTRIDGE files (".car" and ".c01" to ".c70"),
  including decoding the header, showing the stored ROM data checksum and
  computing the actual checksum of the contained ROM data.

  Only the ".cfg" file functionality is specific to "THE400 Mini"; the other
  functions can be used with any Atari 8-bit emulators/systems.


## Usage: ##

    Usage: aemt.py [OPTIONS] COMMAND [ARGS]...
    
      [A]tari [E]ight-bit [M]ulti-[T]ool
    
        Moves files to organized folder structures, with an optionally
        limited number of files per folder.
    
        Creates, applies and updates .cfg files for Atari THE400 Mini
        games on USB media.

	    Identifies and verifies Atari 8-bit cartridge images.
    
    Options:
      --version  Show the version and exit.
      --help     Show this message and exit.
    
    Commands:
      cart    Identifies and validates Atari 8-bit cartridges.
      config  Creates and updates .CFG files for THE400 Mini USB Media games.
      split   Moves files to organized folder structures.

### Notes: 

There is one overall program, "aemt.py", within which mutliple commands and sub-commands are available.	The individual commands are created in a way which allows you to use them	DIRECTLY as if they were their own, self-contained, tools.

So you can use:

	  aemt.py split ...

	or:

	  split.py ...
