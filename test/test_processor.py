import unittest
from app.memory import MemoryController, Rom
import app.processor

# Test that each addressing mode takes the correct amount of cycles
class ProcessorAddressingCycleTest(unittest.TestCase):
    def setUp(self):
        self.memory = app.memory.MemoryController()
        self.processor = app.processor.Processor(self.memory)

    # helper: Tests how much the program counter incremented given an opcode
    def do_counter_test(self, mode, expected):
        @app.processor.instruction(0x00, 'test', mode)
        def test(*args):
            pass

        # Replace the processors instructions with our fake instruction
        instructions = test._instruction_info
        self.processor.instructions = app.processor.InstructionSet(instructions)

        expected = self.processor.program_counter + expected
        self.memory.set_rom(Rom([0x00]))
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.program_counter, expected)

    def test_implied_addressing(self):
        "The program counter should increase by 1 in implied addressing"
        self.do_counter_test('implied', 1)

    def test_absolute_addressing(self):
        "The program counter should increase by 3 in absolute addressing"
        self.do_counter_test('abs', 3)

    def test_absolutex_addressing(self):
        "The program counter should increase by 3 in absolute,X addressing"
        self.do_counter_test('absx', 3)

    def test_absolutey_addressing(self):
        "The program counter should increase by 3 in absolute,Y addressing"
        self.do_counter_test('absy', 3)

    def test_zeropage_addressing(self):
        "The program counter should increase by 2 in zeropage addressing"
        self.do_counter_test('zp', 2)

    def test_zeropagex_addressing(self):
        "The program counter should increase by 2 in zeropage,X addressing"
        self.do_counter_test('zpx', 2)

    def test_zeropagey_addressing(self):
        "The program counter should increase by 2 in zeropage,Y addressing"
        self.do_counter_test('zpy', 2)

    def test_immediate_addressing(self):
        "The program counter should increase by 2 in immediate addressing"
        self.do_counter_test('imm', 2)

# Test that each addressing mode fetches the correct value
# from memory and gives it to the instruction
class ProcessorAddressingModeValueTest(unittest.TestCase):
    def setUp(self):
        self.memory = app.memory.MemoryController()
        self.processor = app.processor.Processor(self.memory)

    # Tests the and instruction given the addressing mode (given as an opcode)
    def do_value_test(self, mode):
        test_value = 35
        self.received_value = None

        @app.processor.instruction(0x00, 'test', mode)
        def test(_, value):
            self.received_value = value

        # Replace the processors instructions with our fake instruction
        instructions = test._instruction_info
        self.processor.instructions = app.processor.InstructionSet(instructions)

        # set up so that immediate works as well
        self.memory.write(0x56, test_value)
        self.memory.set_rom(Rom([0x00, 0x056, 0]))
        self.processor.next_instruction_cycle()
        self.assertEqual(self.received_value, test_value)

    def test_absolute(self):
        "Absolute addressing should pass the value"
        self.do_value_test('abs')

    def test_absolutex(self):
        "Absolute,X addressing should pass the value"
        self.do_value_test('absx')

    def test_absolutey(self):
        "Absolute,Y addressing should pass the value"
        self.do_value_test('absy')

    def test_zeropage(self):
        "Zero page addressing should pass the value"
        self.do_value_test('zp')

    def test_zeropagex(self):
        "Zero page,X addressing should pass the value"
        self.do_value_test('zpx')

    def test_zeropagey(self):
        "Zero page,Y addressing should pass the value"
        self.do_value_test('zpy')

    # TODO: test immediate addressing. We can't just use do_value_test in that case

class InstructionsTest(unittest.TestCase):
    def setUp(self):
        self.memory = app.memory.MemoryController()
        self.processor = app.processor.Processor(self.memory)

    def test_and(self):
        "AND should 'and' a value with the accumulator"
        self.processor.accumulator = 52
        self.memory.set_rom(Rom([0x29, 56, 0])) # and #56
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.accumulator, 56 & 52)

    def test_or(self):
        "OR should 'or' a value with the accumulator"
        self.processor.accumulator = 52
        self.memory.set_rom(Rom([0x09, 56, 0])) # or #56
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.accumulator, 56 | 52)

    def test_lda(self):
        "LDA should load the accumulator with a value"
        self.memory.set_rom(Rom([0xa9, 56, 0]))
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.accumulator, 56)

    def test_ldx(self):
        "LDX should load index X with a value"
        self.memory.set_rom(Rom([0xa2, 56, 0]))
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.x, 56)

    def test_ldy(self):
        "LDY should load index Y with a value"
        self.memory.set_rom(Rom([0xa0, 56, 0]))
        self.processor.next_instruction_cycle()
        self.assertEqual(self.processor.y, 56)
