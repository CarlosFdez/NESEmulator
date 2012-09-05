import functools

import main

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
    def __init__(self, opcode, mnemonic, addressing='implied'):
        self.opcode = opcode
        self.mnemonic = mnemonic
        self.addressing = addressing
        
    def __call__(self, func):
        @functools.wraps(func)
        def wrapped_instruction(*args, **kwargs):
            return func(*args, **kwargs)
            
        wrapped_instruction._instruction_info = Instruction(
            opcode = self.opcode,
            mnemonic = self.mnemonic,
            mode = self.addressing,
            callback = func,
            description = func.__doc__
        )
        
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
        instructions = []
        for func in self.__class__.__dict__.values():
            if callable(func) and hasattr(func, '_instruction_info'):
                instructions.append(func._instruction_info)
        self.instructions = InstructionSet(instructions)
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
        # Todo: Allow the instruction to get the arguments itself
        # Note: data read is unsigned in all modes except relative
        arguments = []
        if mode == 'implied':
            # implied
            pass
        elif mode == 'abs':
            # absolute: cmd $aaaa
            arguments.append(self.memory.read_word(self.program_counter))
            self.program_counter += 2
        elif mode == 'imm':
            # immediate: cmd #$aa
            arguments.append(self.memory.read(self.program_counter))
            self.program_counter += 1
        else:
            raise Exception('Addressing mode %s not recognized' % mode)
        
        instruction.execute(arguments)
    
    @instruction(0x29, 'and', 'imm')
    def and_29(self, value):
        'AND memory with accumulator'
        pass
        
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
    memory = main.MemoryController()
    processor = Processor(memory)
    print processor.instructions