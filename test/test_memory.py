import unittest
import app.memory

class MemoryTest(unittest.TestCase):
    def setUp(self):
        self.memory = app.memory.MemoryController()

    def test_readwrite(self):
        "It should be possible to read and write memory to RAM"
        value = 44  # any arbitrary number
        self.memory.write(0x20, value)
        self.assertEqual(self.memory.read(0x20), value)

    def test_mirror(self):
        "Addresses 0x0000 to 0x07FF should be mirrored 3 times"
        value = 37 # any arbitrary number
        self.memory.write(0x20, value)
        self.assertEqual(self.memory.read(0x20), value)
        self.assertEqual(self.memory.read(0x800 + 0x20), value)
        self.assertEqual(self.memory.read((2 * 0x800) + 0x20), value)
        self.assertEqual(self.memory.read((3 * 0x800) + 0x20), value)

if __name__ == '__main__':
    unittest.main()
