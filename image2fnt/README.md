# [Image2Fnt](https://github.com/idunmore/AtariTools/tree/main/image2fnt) - Image to Font Converter

This is a command-line tool for converting losslessly-encoded bitmap files (e.g., .PNG and .GIF) to Atari 8-bit binary .FNT files. The goal is to allow **almost any** image, sprite, character set or bitmap font editor to be used to create Atari 8-bit font/character sets in .FNT format:

    Usage: image2fnt.py [OPTIONS] COMMAND [ARGS]...
    
      Converts bitmapped images to Atari 8-bit .FNT files.
    
    Options:   --version  Show the version and exit.
               --help     Show this message and exit.
        
    Commands:   convert  Converts bitmapped images to Atari 8-bit .FNT files.
                info     Displays image metrics, color/palette data, and character layout.

It supports character sets using either 1 or 2 bits per pixel, from sources using 1:1 or 2:1 pixel aspect ratios, and 64 or 128 characters per set.  This allows conversion of .FNT files for ANTIC modes 2, 4, 5, 6 and 7 (BASIC Graphics modes 0, 12*, 13*, 1 and 2 respectively).


## Source Files
.FNT files can be created from losslessly-encoded bit-map files (e.g., .PNG and .GIF) of either 256x32 pixels (32 characters by 4 rows, for 128 characters total) or 128x64 pixels (16 characters by 8 rows), or, for 2:1 aspect ration files, 128x32 and 64x64 pixel formats.

***Note**: The 32x4 and 16x8 character layouts are common layouts for Atari .FNT editors.  Other layouts are possible, and should be detected automatically - provided either 128 or 64 characters are present, and they are presented in rows with the same number of characters in each.*


## Templates
The [templates ](https://github.com/idunmore/AtariTools/tree/main/image2fnt/templates) folder contains blank template files for both 32x4 and 16x8 format character sets.

 - .XCF format are intended for the [GIMP](https://www.gimp.org) 2.10 and later. 
 - .PSD format files are intended for [Adobe](https://www.adobe.com) [Photoshop](https://www.adobe.com/products/photoshop.html). 

### Using the .XCF Templates

Open the **template** in GIMP. 

Under the **VIEW** menu:  

1.  Turn OFF “Show Layer Boundary” (optional)
2.  Turn ON “Show Grid”
3.  Zoom 1600:1 (or whatever you prefer)

When **SAVING**:  

Under the "FILE" menu, choose "Export as"

 1. Choose “GIF Image” as the File Format.
 2. When prompted, select “Crop”
 3. Uncheck “GIF comment”

When **EDITING**:

If you want a different grid color:  

Under the **IMAGE** menu:

1.  Select “Configure Grid”
2.  Click “Foreground Color” to choose a new grid-line color.
3.  Click “OK”
4.  Click “OK”


## Fonts

The [fonts](https://github.com/idunmore/AtariTools/tree/main/image2fnt/fonts) folder contains example fonts both as native files (.XCF and .PSD), exported versions in convertible file formats (e.g. .GIF and .PNG), as well as .FNT files created for them by the [Image2Fnt](https://github.com/idunmore/AtariTools/tree/main/image2fnt) tool.

The [ATARI 800 - System Character Set (32x4).xcf](https://github.com/idunmore/AtariTools/blob/main/image2fnt/fonts/ATARI%20800%20-%20System%20Character%20Set%20%2832x4%29.xcf) file can also be used as a template for creating new fonts, while also providing a reference for the proper positions for each character, as defined for the Atari System character set.

## .FNT File Format

.FNT files are comprised of 128 character definitions, each 8-bits wide by 8-scan-lines tall, and beginning with the 8-bit bitmap (byte) for the top most scan-line of  character 0.  The 9th byte (index 8) in the .FNT file would be the first scan-line for the 2nd character, etc.

---
*Atari XL/XE only (equivalent ANTIC modes are available on all models).
