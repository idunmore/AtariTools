# AtariTools
A collection of tools for Atari computers, consoles and emulators.

## Atari 8-bit Tools
Tools for the various Atari 8-bit machines, including the 400, 800, 800XL, 130XE computers, the 5200 console, as well various emulators such as [Atari800](https://atari800.github.io)/[Atari800MacX](https://www.atarimac.com/atari800macx.php), [Altirra](https://www.virtualdub.org/altirra.html), and plug-and-play units such as [THE400 Mini](https://atari.com/products/atari-400-mini-1):

### [AEMT](https://github.com/idunmore/AtariTools/tree/main/aemt) - Atari Eight-bit Multi-Tool

[\[A\]tari \[E\]ight-bit \[M\]ulti-\[T\]ool](https://github.com/idunmore/AtariTools/tree/main/aemt)

This is a command-line tool, intended to provide some "quality of life" improvements to managing large game/program libraries, on USB Media, for the "Atari THE400 Mini" (with utilities for other Atari 8-bit emulators).

Current functionality includes:

-   Moving files, in bulk, to organized folder structures.
    
-   Creating, applying, and updating .cfg files automatically.
    
-   Identify and validate CARTRIDGE files.


### [Fnt2Data](https://github.com/idunmore/AtariTools/tree/main/fnt2data) - Font to Data Converter

This is a command-line tool for converting Atari 8-bit binary .FNT files into "data" statements for various Atari 8-bit/6502 Assemblers and programming languages (e.g. Atari BASIC).

.FNT files are comprised of 128 character definitions, each 8-bits wide by 8-scan-lines tall, and beginning with the 8-bit bitmap (byte) for the top most scan-line of  character 0.  The 9th byte (index 8) in the .FNT file would be the first scan-line for the 2nd character, etc.

Output is a series of "data" statements, such as (data for first 2 characters):

.BYTE $00, $00, $00, $00, $00, $00, $00, $00, $38, $38, $38, $10, $00, $38, $38, $00


## Atari Gamestation Pro Tools
Tools for the [Atari Gamestation Pro](https://atari.com/products/atari-gamestation-pro) plug-and-play console:

### [ABAT](https://github.com/idunmore/AtariTools/tree/main/abat) - AGSP Box Art Tool
[\[A\]tari Gamestation Pro \[B\]ox \[A\]rt \[T\]ool](https://github.com/idunmore/AtariTools/tree/main/abat)

A command-line tool for fetching, cropping and resizing box art for Atari 2600, 5200 and 7800 cartridges for use in the main menu of the Atari Gamestation Pro.
