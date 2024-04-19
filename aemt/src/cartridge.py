# cartridge.py - Atari 8-bit Cartridge Utility & Functions
#
# Copyright(C) 2024, Ian Michael Dunmore
#
# License: https://github.com/idunmore/AtariTools/blob/master/LICENSE

# Native Python Modules

import enum
import pathlib
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

# General Constants
BYTES_PER_KILOBYTE = 1024

# MSB (Most Significant Bit) Constants
MSB_DIGIT_1 = 256 * 256 * 256
MSB_DIGIT_2 = 256 * 256
MSB_DIGIT_3 = 256
MSB_DIGIT_4 = 1

# Cartridge Constants

CHECKSUM_MASK = 0x000000FF
FIRST_CARTRIDGE_TYPE = 1
LAST_CARTRIDGE_TYPE = 70
CART_HEADER_SIZE = 16
CART_PREAMBLE = 'CART'

SIG_OFFSET = 0
SIG_LENGTH = 4
TYPE_OFFSET = 4
TYPE_LENGTH = 4
CHECKSUM_OFFSET = 8
CHECKSUM_LENGTH = 4
IMAGE_OFFSET = 16

# Machines Types
class Machine(enum.Enum):
    '''Atari 8-bit Cartridge Machine Types'''
    ATARI_800_XL_XE = 0
    '''Atari 400, 800, 800XL, 1200XL, 600XL, 65XE, 130XE, 800XE, XEGS, and
    compatible machines.'''
    ATARI_800 = 1
    '''Atari 800-Specific - Typically RIGHT SLOT cartridges.'''
    ATARI_5200 = 2

# Cartridge Type Class
class CartridgeType:
    '''Cartridge Type & Details'''
    def __init__(self: Self, type: int, size_kilobytes: int,
        machine: Machine, description: str):        

        if type < FIRST_CARTRIDGE_TYPE or type > LAST_CARTRIDGE_TYPE:
            raise ValueError(f'Invalid cartridge Type: {type}')
        self._type = type

        if (size_kilobytes > BYTES_PER_KILOBYTE and
            size_kilobytes % BYTES_PER_KILOBYTE != 0):
            raise ValueError(f'Invalid cartridge size: {size_kilobytes}')        
        self._size_kilobytes = size_kilobytes

        self._machine = machine
        self._description = description        

    @property
    def id(self: Self) -> int:
        return self._id
    
    @property
    def size_kilobytes(self: Self) -> int:
        return self._size_kilobytes
    
    @property
    def machine(self: Self) -> str:
        return self._machine
    
    @property
    def description(self: Self) -> str:
        return self._description
    
# Currently (04/19/24) known cartridge ID/types
cart_types = {
    1: CartridgeType(1, 8,  Machine.ATARI_800_XL_XE, 'Standard 8 KB cartridge', ),
    2: CartridgeType(2, 16, Machine.ATARI_800_XL_XE, 'Standard 16 KB cartridge'),
    3: CartridgeType(3, 16, Machine.ATARI_800_XL_XE, 'OSS two-chip 16 KB cartridge'),        
    4: CartridgeType(4, 32, Machine.ATARI_5200, 'Standard 32 KB 5200 cartridge'),
    5: CartridgeType(5, 32, Machine.ATARI_800_XL_XE, 'DB 32 KB cartridge'),
    6: CartridgeType(6, 16, Machine.ATARI_5200, 'Two chip 16 KB 5200 cartridge'),
    7: CartridgeType(7, 40, Machine.ATARI_5200, 'Bounty Bob Strikes Back 40 KB 5200 cartridge'),   
    8: CartridgeType(8, 64, Machine.ATARI_800_XL_XE, '64 KB Williams cartridge'),
    9: CartridgeType(9, 64, Machine.ATARI_800_XL_XE, 'Express 64 KB cartridge'),
    10: CartridgeType(10, 64, Machine.ATARI_800_XL_XE, 'Diamond 64 KB cartridge'),
    11: CartridgeType(11, 64, Machine.ATARI_800_XL_XE, 'SpartaDOS X 64 KB cartridge'),
    12: CartridgeType(12, 32, Machine.ATARI_800_XL_XE, 'XEGS 32 KB cartridge'),
    13: CartridgeType(13, 64, Machine.ATARI_800_XL_XE, 'XEGS 64 KB cartridge (banks 0-7)'),
    14: CartridgeType(14, 128, Machine.ATARI_800_XL_XE, 'XEGS 128 KB cartridge'),
    15: CartridgeType(15, 16, Machine.ATARI_800_XL_XE, 'OSS one chip 16 KB cartridge'),
    16: CartridgeType(16, 16, Machine.ATARI_5200, 'One chip 16 KB 5200 cartridge'),
    17: CartridgeType(17, 128, Machine.ATARI_800_XL_XE, 'Decoded Atrax 128 KB cartridge'),
    18: CartridgeType(18, 40, Machine.ATARI_800_XL_XE, 'Bounty Bob Strikes Back 40 KB cartridge'),
    19: CartridgeType(19, 8, Machine.ATARI_5200, 'Standard 8 KB 5200 cartridge'),
    20: CartridgeType(20, 4, Machine.ATARI_5200, 'Standard 4 KB 5200 cartridge'),
    21: CartridgeType(21, 8, Machine.ATARI_800, 'Right slot 8 KB cartridge'),
    22: CartridgeType(22, 32, Machine.ATARI_800_XL_XE, '32 KB Williams cartridge'),
    23: CartridgeType(23, 256, Machine.ATARI_800_XL_XE, 'XEGS 256 KB cartridge'),
    24: CartridgeType(24, 512, Machine.ATARI_800_XL_XE, 'XEGS 512 KB cartridge'),
    25: CartridgeType(25, 1024, Machine.ATARI_800_XL_XE, 'XEGS 1 MB cartridge'),
    26: CartridgeType(26, 16, Machine.ATARI_800_XL_XE, 'MegaCart 16 KB cartridge'),
    27: CartridgeType(27, 32, Machine.ATARI_800_XL_XE, 'MegaCart 32 KB cartridge'),
    28: CartridgeType(28, 64, Machine.ATARI_800_XL_XE, 'MegaCart 64 KB cartridge'),
    29: CartridgeType(29, 128, Machine.ATARI_800_XL_XE, 'MegaCart 128 KB cartridge'),
    30: CartridgeType(30, 256, Machine.ATARI_800_XL_XE, 'MegaCart 256 KB cartridge'),
    31: CartridgeType(31, 512, Machine.ATARI_800_XL_XE, 'MegaCart 512 KB cartridge'),
    32: CartridgeType(32, 1024, Machine.ATARI_800_XL_XE, 'MegaCart 1 MB cartridge'),
    33: CartridgeType(33, 32, Machine.ATARI_800_XL_XE, 'Switchable XEGS 32 KB cartridge'),
    34: CartridgeType(34, 64, Machine.ATARI_800_XL_XE, 'Switchable XEGS 64 KB cartridge'),
    35: CartridgeType(35, 128, Machine.ATARI_800_XL_XE, 'Switchable XEGS 128 KB cartridge'),
    36: CartridgeType(36, 256, Machine.ATARI_800_XL_XE, 'Switchable XEGS 256 KB cartridge'),
    37: CartridgeType(37, 512, Machine.ATARI_800_XL_XE, 'Switchable XEGS 512 KB cartridge'),
    38: CartridgeType(38, 1024, Machine.ATARI_800_XL_XE, 'Switchable XEGS 1 MB cartridge'),
    39: CartridgeType(39, 8, Machine.ATARI_800_XL_XE, 'Phoenix 8 KB cartridge'),
    40: CartridgeType(40, 16, Machine.ATARI_800_XL_XE, 'Blizzard 16 KB cartridge'),
    41: CartridgeType(41, 128, Machine.ATARI_800_XL_XE, 'Atarimax 128 KB Flash cartridge'),
    42: CartridgeType(42, 1024, Machine.ATARI_800_XL_XE, 'Atarimax 1 MB Flash cartridge'),
    43: CartridgeType(43, 128, Machine.ATARI_800_XL_XE, 'SpartaDOS X 128 KB cartridge'),
    44: CartridgeType(44, 8, Machine.ATARI_800_XL_XE, 'OSS 8 KB cartridge'),
    45: CartridgeType(45, 16, Machine.ATARI_800_XL_XE, 'OSS two chip 16 KB cartridge (043M)'),
    46: CartridgeType(46, 4, Machine.ATARI_800_XL_XE, 'Blizzard 4 KB cartridge'),
    47: CartridgeType(47, 32, Machine.ATARI_800_XL_XE, 'AST 32 KB cartridge'),
    48: CartridgeType(48, 64, Machine.ATARI_800_XL_XE, 'Atrax SDX 64 KB cartridge'),
    49: CartridgeType(49, 128, Machine.ATARI_800_XL_XE, 'Atrax SDX 128 KB cartridge'),
    50: CartridgeType(50, 64, Machine.ATARI_800_XL_XE, 'Turbosoft 64 KB cartridge'),
    51: CartridgeType(51, 128, Machine.ATARI_800_XL_XE, 'Turbosoft 128 KB cartridge'),
    52: CartridgeType(52, 32, Machine.ATARI_800_XL_XE, 'Ultracart 32 KB cartridge'),
    53: CartridgeType(53, 8, Machine.ATARI_800_XL_XE, 'Low bank 8 KB cartridge'),
    54: CartridgeType(54, 128, Machine.ATARI_800_XL_XE, 'SIC! 128 KB cartridge'),
    55: CartridgeType(55, 256, Machine.ATARI_800_XL_XE, 'SIC! 256 KB cartridge'),
    56: CartridgeType(56, 512, Machine.ATARI_800_XL_XE, 'SIC! 512 KB cartridge'),
    57: CartridgeType(57, 2, Machine.ATARI_800_XL_XE, 'Standard 2 KB cartridge'),
    58: CartridgeType(58, 4, Machine.ATARI_800_XL_XE, 'Standard 4 KB cartridge'),
    59: CartridgeType(59, 4, Machine.ATARI_800, 'Right slot 4 KB cartridge'),
    60: CartridgeType(60, 32, Machine.ATARI_800_XL_XE, 'Blizzard 32 KB cartridge'),
    61: CartridgeType(61, 2048, Machine.ATARI_800_XL_XE, 'MegaMax 2 MB cartridge'),
    62: CartridgeType(62, 128*1024, Machine.ATARI_800_XL_XE, 'The!Cart 128 MB cartridge'),
    63: CartridgeType(63, 4096, Machine.ATARI_800_XL_XE, 'Flash MegaCart 4 MB cartridge'),
    64: CartridgeType(64, 2048, Machine.ATARI_800_XL_XE, 'MegaCart 2 MB cartridge'),
    65: CartridgeType(65, 32*1024, Machine.ATARI_800_XL_XE, 'The!Cart 32 MB cartridge'),
    66: CartridgeType(66, 64*1024, Machine.ATARI_800_XL_XE, 'The!Cart 64 MB cartridge'),
    67: CartridgeType(67, 64, Machine.ATARI_800_XL_XE, 'XEGS 64 KB cartridge (banks 8-15)'),
    68: CartridgeType(68, 128, Machine.ATARI_800_XL_XE, 'Atrax 128 KB cartridge'),
    69: CartridgeType(69, 32, Machine.ATARI_800_XL_XE, 'aDawliah 32 KB cartridge'),
    70: CartridgeType(70, 64, Machine.ATARI_800_XL_XE, 'aDawliah 64 KB cartridge')
}

class CartridgeHeader:
    def __init__(self: Self, bytes: bytes):
        if (len(bytes)) < CART_HEADER_SIZE:
            raise ValueError(
                f'Invalid cartridge header size; expected: {CART_HEADER_SIZE} '
                f'bytes, got: {len(bytes)}')
        self._raw_bytes = bytes
        self._invalid_reason = None

    @property
    def signature(self: Self) -> str:
        sig = self._raw_bytes[SIG_OFFSET:SIG_LENGTH]
        return f'{chr(sig[0])}{chr(sig[1])}{chr(sig[2])}{chr(sig[3])}'
    
    @property
    def type(self: Self) -> int:
        type = self._raw_bytes[TYPE_OFFSET:TYPE_OFFSET + TYPE_LENGTH]
        return ((type[0] * MSB_DIGIT_1) + (type[1] * MSB_DIGIT_2) +
                (type[2] * MSB_DIGIT_3) + (type[3] * MSB_DIGIT_4))        
    
    @property
    def checksum(self: Self) -> int:
        checksum = (
            self._raw_bytes[CHECKSUM_OFFSET:CHECKSUM_OFFSET + CHECKSUM_LENGTH])
        return ((checksum[0] * MSB_DIGIT_1) + (checksum[1] * MSB_DIGIT_2) +
                (checksum[2] * MSB_DIGIT_3) + (checksum[3] * MSB_DIGIT_4))        
    
    @property
    def is_valid(self: Self) -> bool:
        if self.signature != CART_PREAMBLE:
            self._invalid_reason = 'Invalid signature'
            return False
        if self.type not in cart_types:
            self._invalid_reason = 'Invalid cartridge type'
            return False
        if self.checksum != compute_checksum(self._raw_bytes[IMAGE_OFFSET:]):
            self._invalid_reason = 'Header checksum mismatch with cartridge'
            return False
        
        self._invalid_reason = None
        return True
    
    @property
    def invalid_reason(self: Self) -> str:
        '''Reason cartridge is invalid, if any; otherwise None'''
        # Invoke "is_valid" to set the invalid reason
        is_valid = self.is_valid
        return self._invalid_reason

# General Atari Functions
def compute_checksum(bytes: bytes) -> int:
    '''Computes the .car checksum for a sequence of bytes'''
    result = 0
    for byte in bytes:
        result += byte & CHECKSUM_MASK
    return result

@click.group()
@click.version_option('0.0.0.1')
def cart():
    '''Identifies and validates Atari 8-bit cartridges.'''
    pass

@cart.command('id')
def id():
    pass

@cart.command('verify')
@click.argument('filename', type=click.Path(exists=True))
def verify(filename: str):
    '''Verifies the cartridge header, compares the header checksum to the
    actual checksum of the cartridge data, and compares indicated cartridge type
    to the size of the cartridge image.'''
    file = pathlib.Path(filename)
    data = file.read_bytes()
    header = CartridgeHeader(data)
    actual_checksum = compute_checksum(data[CART_HEADER_SIZE:])
    print(f'Header: {header.signature} Type: {header.type} Checksum: 0x{header.checksum:08x} Actual: 0x{actual_checksum:08x}')
    print(f'Is Valid: {header.is_valid} Reason: {header.invalid_reason}')
    print(f'Description: {cart_types[header.type].description}')
    

# Run!
if __name__ == '__main__':
    cart()