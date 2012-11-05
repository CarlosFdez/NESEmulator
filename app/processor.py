import functools

# Represents a special purpose register used internally by the processor
# Internally, the data is laid out as follows:
# (high) N | V | 1 | B | D | I | Z | C (low)
#   C - Carry
#   Z - Zero
#   I - IRQ Disable
#   D - Binary Decimal Mode. Its value is ignored by the NES
#   B - Brk command
#   V - overflow. If adding two positives creates a negative or vice versa,
#       this flag will be set
#   N - negative
class ProcessorStatus(object):
    def __init__(self):
        self.carry = 0
        self.zero = 0
        self.irq_disable = 0
        self.decimal_mode = 0 # ignored
        self.brk_command = 0
        self.overflow = 0
        self.negative = 0

# A decorator to ease implementation of processor instructions
# TODO: Allow stacking of decorators
class instruction(object):
    # Todo: Add an arguent for retrieving address instead of value
    def __init__(self, opcode, mnemonic, addressing='implied'):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.addressing = addressing

    def __call__(self, func):
        @functools.wraps(func)
        def wrapped_instruction(*args, **kwargs):
            return func(*args, **kwargs)

        if hasattr(func, '_instruction_info'):
            wrapped_instruction._instruction_info = func._instruction_info
        else:
            wrapped_instruction._instruction_info = []

        # TODO: Instead of using func, use the callback from the first instruction info
        # for efficiency reasons
        wrapped_instruction._instruction_info.append(Instruction(
            opcode = self.opcode,
            mnemonic = self.mnemonic,
            mode = self.addressing,
            callback = func,
            description = func.__doc__
        ))

        return wrapped_instruction

class Instruction(object):
    def __init__(self, opcode, mnemonic, mode, description, callback):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.mode = mode
        self.description = description
        self.callback = callback

    def execute(self, arguments):
        # todo: check if this calls the function on the processor class
        self.callback(*arguments)

    def __str__(self):
        opcode = self.opcode
        mnemonic = self.mnemonic
        mode = self.mode
        description = self.description
        return '%02x %s %-07s %s' % (opcode, mnemonic, mode, description)

# The set of all instructions the processor can perform
class InstructionSet(object):
    def __init__(self, instruction_list):
        self._instructions = instruction_list
        self._opcode_hash = {}
        for instr in instruction_list:
            self._opcode_hash[instr.opcode] = instr

    def find_by_opcode(self, opcode):
        return self._opcode_hash[opcode]

    def find_by_mnemonic_and_mode(self, mnemonic, mode):
        # todo: make this more efficient
        for instruction in self._instructions:
            if instruction.mode == mode and instruction.mnemonic == mnemonic:
                return instruction
        return None

    def __str__(self):
        str_list = map(lambda x: str(x), self._instructions)
        return '\n'.join(str_list)

# NTSC uses the Ricoh 2A03 (RP2A03) and PAL uses the Ricoh 2A07 (RP2A07)
# They are based off the MOS 6502, but lack binary-coded decimal mode.
# It also adds 22 memory mapped IO registers as well.
#
# http://nesdev.parodius.com/6502guid.txt
class Processor(object):
    def __init__(self, memory):
        instructionList = []
        for func in self.__class__.__dict__.values():
            if callable(func) and hasattr(func, '_instruction_info'):
                instructionList.extend(func._instruction_info)
        self.instructions = InstructionSet(instructionList)
        self.memory = memory

        # registers
        self.program_counter = self.memory.rom_start()
        self.x = 0
        self.y = 0
        self.accumulator = 0

    # Executes the next instruction
    # The current implementation decodes the next instruction but does not
    # make any attempt to cache that information.
    # TODO: Finish implementing this
    def next_instruction_cycle(self):
        opcode = self.memory.read(self.program_counter)
        self.program_counter += 1

        instruction = self.instructions.find_by_opcode(opcode)
        mode = instruction.mode

        # Read the next bytes according to the mode
        # Todo: Allow the instruction to get an address instead of the value if it wants
        # Todo: Chain of if statements is slow. Change this
        # Note: data read is unsigned in all modes except relative
        arguments = [self]
        if mode == 'implied':
            # implied - no arguments
            pass
        elif mode == 'abs':
            # absolute: cmd $aaaa
            addr = self.memory.read_word(self.program_counter)
            arguments.append(self.memory.read(addr))
            self.program_counter += 2
        elif mode == 'absx':
            # absolute + X register: cmd $aaaa, X
            addr = self.memory.read_word(self.program_counter) + self.x
            arguments.append(self.memory.read(addr))
            self.program_counter += 2
        elif mode == 'absy':
            # absolute + Y register: cmd $aaaa, Y
            addr = self.memory.read_word(self.program_counter) + self.y
            arguments.append(self.memory.read(addr))
            self.program_counter += 2
        elif mode == 'zp':
            # zero page: cmd $aa
            addr = self.memory.read(self.program_counter)
            arguments.append(self.memory.read(addr))
            self.program_counter += 1
        elif mode == 'zpx':
            # zero page + X register: cmd $aa, X
            addr = self.memory.read(self.program_counter) + self.x
            arguments.append(self.memory.read(addr))
            self.program_counter += 1
        elif mode == 'imm':
            # immediate: cmd #$aa
            value = self.memory.read(self.program_counter)
            arguments.append(value)
            self.program_counter += 1
        else:
            raise Exception('Addressing mode %s not recognized' % mode)

        instruction.execute(arguments)

    # Missing some addressing modes
    @instruction(0x29, 'and', 'imm')
    @instruction(0x25, 'and', 'zp')
    @instruction(0x2d, 'and', 'abs')
    @instruction(0x35, 'and', 'zpx')
    @instruction(0x3d, 'and', 'absx')
    @instruction(0x39, 'and', 'absy')
    def and_addr(self, value):
        'And memory with accumulator'
        self.accumulator &= value

    @instruction(0x69, 'adc', 'imm')
    def adc_69(self, value):
        'Add memory to accumulator with carry'
        pass

    @instruction(0x80, 'sta', 'abs')
    def sta_80(self, address):
        'Store accumulator in memory'
        pass

    @instruction(0xA9, 'lda', 'imm')
    def lda_a9(self, value):
        'Load accumulator with memory'
        pass

if __name__ == '__main__':
    import memory
    memory = memory.MemoryController()
    processor = Processor(memory)
    print(processor.instructions)
