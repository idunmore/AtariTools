### [Image2Data](https://github.com/idunmore/AtariTools/tree/main/image2fnt) - Image to Font Converter

This is a command-line tool for converting losslessly-encoded bitmap files (e.g., .PNG and .GIF) to Atari 8-bit binary .FNT files. The goal is to allow almost any image, sprite, character set or bitmap font editor to be used to create Atari 8-bit font/character sets in .FNT format.

It supports character sets using either 1 or 2 bits per pixel and 64 or 128 characters per set.  This allows conversion of .FNT files for ANTIC modes 2, 4, 5, 6 and 7 (BASIC Graphics modes 0, 12*, 13*, 1 and 2 respectively).

.FNT files are comprised of 128 character definitions, each 8-bits wide by 8-scan-lines tall, and beginning with the 8-bit bitmap (byte) for the top most scan-line of  character 0.  The 9th byte (index 8) in the .FNT file would be the first scan-line for the 2nd character, etc.

---
*Atari XL/XE only (equivalent ANTIC modes are available on all models).
