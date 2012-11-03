import unittest
from app.memory import MemoryController, Rom
import app.processor

# Tests how much the program counter incremented given an opcode
def test_counter_increase(tester, opcode, expected):
    expected = tester.processor.program_counter + expected
    tester.memory.set_rom(Rom([opcode]))
    tester.processor.next_instruction_cycle()
    tester.assertEqual(tester.processor.program_counter, expected)

class ProcessorCycleTest(unittest.TestCase):
    def setUp(self):
        self.memory = app.memory.MemoryController()
        self.processor = app.processor.Processor(self.memory)

    # TODO: Test implied once an implied address instruction gets implemented

    def test_absolute_addressing(self):
        "The program counter should increase by 3 in absolute addressing"
        test_counter_increase(self, 0x2d, 3) # and

    def test_absolutex_addressing(self):
        "The program counter should increase by 3 in absolute,X addressing"
        test_counter_increase(self, 0x3d, 3) # and

    def test_absolutey_addressing(self):
        "The program counter should increase by 3 in absolute,Y addressing"
        test_counter_increase(self, 0x39, 3) # and

    def test_zeropage_addressing(self):
        "The program counter should increase by 2 in zeropage addressing"
        test_counter_increase(self, 0x25, 2) # and

    def test_zeropagex_addressing(self):
        "The program counter should increase by 2 in zeropage,X addressing"
        test_counter_increase(self, 0x35, 2) # and

    def test_immediate_addressing(self):
        "The program counter should increase by 2 in immediate addressing"
        test_counter_increase(self, 0xA9, 2) # lda
