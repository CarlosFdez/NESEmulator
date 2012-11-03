import io
import struct

# http://nesdev.parodius.com/NESDoc.pdf

# This class represents the memory controller hardware in the NES. Memory
# is little endian, therefore $1234 is stored as [$34] and then [$12]
#
# The NES hardware uses memory mapped IO, which is laid out as follows:
# 0000 - 07FF    RAM (First 256 bytes is zero page)
# 0800 - 0FFF    RAM Mirror #1
# 1000 - 17FF    RAM Mirror #2
# 1800 - 1FFF    RAM mirror #3
# 2000 - 2007    I/O Registers
# 2008 - 3FFF    Continous Mirrors of previous registers
# 4000 - 401F    I/O Registers (new ones)
# 4020 - 5FFF    Expansion ROM (apparently extra memory for MMC5)
# 6000 - 7FFF    SRAM (Save RAM)
# 8000 - BFFF    PRG-ROM (Program ROM)
# C000 - FFFF    PRG-ROM (Program ROM)
class MemoryController(object):
    def __init__(self, rom = None):
        self._rom = rom
        self.ram = [0] * 0x800

    # Sets the file pointer location
    def set_pointer_to(self, address):
        self.mem_location = address

    # Where to start program execution
    def rom_start(self):
        return 0x8000

    # Reads an unsigned byte from memory. The memory is obtained from the
    # pointer location/address
    def read(self, address):
        if address < 0x2000:
            # Read from RAM
            return self.ram[address % 0x800]
        if address < 0x8000:
            print('WARNING: NOT SUPPORTED')
        else:
            rom_location = address - 0x8000
            return self._rom.prg_rom[rom_location]

    # Reads an unsigned word from memory
    # Note: The implementation is fairly dumb
    def read_word(self, address):
        low = self.read(address)
        high = self.read(address + 1)
        return (high << 8) + low

    def write(self, address, value):
        if address < 0x2000:
            # Write to RAM
            self.ram[address % 0x800] = value

# LOADER INFORMATION - Something about how the PRG-ROM banks are treated, and
# which bank to load in memory

# This class represents the stack in the NES hardware. The stack
# is a top down stack which is located in memory locations $0100 - $01FF
# (after the zero page)
#
# There is no detection of overflow and the pointer merely wraps from $00 to $FF.
# PS: How is it actually laid out? I assume the pointer starts at 0 and points
# to the topmost item
class Stack(object):
    def __init__(self, memory_controller):
        self.memory = memory_controller

# A class to simplify file io internally. This should be replaced for a valid
# module
class ByteReader(object):
    # Takes a file opened with open()
    def __init__(self, file):
        self._file = file

    def read_str(self, length):
        return self._file.read(length)

    def next(self):
        return self.read(1)[0]

    # Reads length unsigned bytes into a tuple
    def read(self, length=1):
        data = self._file.read(length)
        # Todo: if len(data) != length, there's a problem
        return struct.unpack('B' * length, data)


def read_rom_from_file(filename):
    with io.open(filename, mode='rb') as f:
        f = ByteReader(f)
        if f.read_str(3) != 'NES' or f.next() != 0x1A:
            print('ERROR: NOT A NES FILE')
        num_rom_banks = f.next()
        num_vrom_banks = f.next()
        f.next() # Control byte 1 is ignored for now
        f.next() # Control byte 2 is ignored for now
        num_ram_banks = f.next()
        if not num_ram_banks:
            num_rank_banks = 1
        f.read(7) # Should all be 0

        # NOTE: Add trainer support

        # Each PRG ROM Bank is 16KB
        # Each CHR-ROM / VROM bank is 8KB
        prg_rom = f.read(num_rom_banks * 16 * (2**10))
        chr_rom = f.read(num_vrom_banks * 8 * (2**10))
        return Rom(
            prg_rom = prg_rom,
            chr_rom = chr_rom
        )

class Rom(object):
    def __init__(self, prg_rom=(), chr_rom=()):
        self.prg_rom = prg_rom
        self.chr_rom = chr_rom

class Emulator(object):
    def __init__(self):
        pass

    def set_rom(self, rom):
        self._rom = rom

    def start_emulation(self):
        self.memory_controller = MemoryController(rom=self._rom)


