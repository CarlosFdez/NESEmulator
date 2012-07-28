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

def instruction(opcode, mnemonic, addressing='Implied'):
    def wrapped(func):
        @functools.wraps(func)
        def wrapped_instruction(*args, **kwargs):
            return func(*args, **kwargs)
            
        wrapped_instruction._instruction_info = {
            'opcode': opcode,
            'mnemonic': mnemonic,
            'mode': addressing
        }
        return wrapped_instruction
    return wrapped

# The set of all instructions the processor can perform
class InstructionSet(object):
    def __init__(self, instruction_list):
        self._instructions = instruction_list
        self._opcode_hash = {}
        for instr in instruction_list:
            self._opcode_hash[instr['opcode']] = instr
        
    def find_by_opcode(self, opcode):
        return self._opcode_hash[opcode]
        
    def __str__(self):
        return self._instructions.__str__()

# NTSC uses the Ricoh 2A03 (RP2A03) and PAL uses the Ricoh 2A07 (RP2A07)
# They are based off the MOS 6502, but lack binary-coded decimal mode.
# It also adds 22 memory mapped IO registers as well
#
# http://nesdev.parodius.com/6502guid.txt
class Processor(object):
    def __init__(self):
        instructions = []
        for func in self.__class__.__dict__.values():
            if callable(func) and hasattr(func, '_instruction_info'):
                instructions.append(func._instruction_info)
        self._instructions = InstructionSet(instructions)
    
    @instruction(0x4E, 'sei')
    def sei(self):
        pass
        
    @instruction(0x8D, 'sta', 'abs')
    def sta_8d(self, address):
        pass
    
    @instruction(0xA2, 'ldx', 'imm')
    def ldx_a2(self, value):
        pass
    
    @instruction(0xA9, 'lda', 'imm')
    def lda_a9(self, value):
        pass
        
    @instruction(0xD8, 'cld')
    def cld(self):
        pass

if __name__ == '__main__':
    processor = Processor()
    print processor._instructions