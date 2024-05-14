### [Fnt2Data](https://github.com/idunmore/AtariTools/tree/main/fnt2data) - Font to Data Converter

This is a command-line tool for converting Atari 8-bit binary .FNT files into "data" statements for various Atari 8-bit/6502 Assemblers and programming languages (e.g. Atari BASIC).

.FNT files are comprised of 128 character definitions, each 8-bits wide by 8-scan-lines tall, and beginning with the 8-bit bitmap (byte) for the top most scan-line of  character 0.  The 9th byte (index 8) in the .FNT file would be the first scan-line for the 2nd character, etc.

Output is a series of "data" statements, such as (data for first 2 characters):

.BYTE $00, $00, $00, $00, $00, $00, $00, $00, $38, $38, $38, $10, $00, $38, $38, $00
