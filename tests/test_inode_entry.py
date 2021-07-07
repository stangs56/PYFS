import unittest

from pyfs import InodeEntry
from pyfs.constants import INODE_ENTRY_SIZE

from tests.test_common import create_dir_if_not_exists, log_with_debug, log_test_case

class TestInodeEntry(unittest.TestCase):
    def setUp(self) -> None:
        self.inode_entry = InodeEntry(bytes(INODE_ENTRY_SIZE))

    def test_init(self):
        self.assertRaises(ValueError, InodeEntry, bytes(1))

    def test_data(self):
        self.assertEqual(self.inode_entry.data, bytes(INODE_ENTRY_SIZE))
        self.inode_entry.data = (b'\xff'*INODE_ENTRY_SIZE)
        self.assertEqual(self.inode_entry.data, (b'\xff'*INODE_ENTRY_SIZE))

    def test_flags(self):
        for i in range(256):
            self.inode_entry.flags = i
            self.assertEqual(self.inode_entry.flags, i)

        with self.assertRaises(OverflowError):
            self.inode_entry.flags = 257

    def test_get_bit_flag(self):
        self.inode_entry.entry_flags = {tmp : 1 << tmp for tmp in range(8)}

        for flags in range(0xff):
            self.inode_entry.flags = flags
            for cur_bit in range(8):
                self.assertEqual(self.inode_entry.get_bit_flag(cur_bit), bool(flags & (1 << cur_bit)), f"Flags set to {flags:>08b} on bit {cur_bit}")
        
        with self.assertRaises(KeyError):
            self.inode_entry.get_bit_flag('KeyThatDoesn\'tExists')

    def test_set_bit_flag(self):
        self.inode_entry.entry_flags = {tmp : 1 << tmp for tmp in range(8)}

        for flags in range(0xff):
            for cur_bit in range(8):
                self.inode_entry.set_bit_flag(cur_bit, bool(flags & (1 << cur_bit)))
            self.assertEqual(self.inode_entry.flags, flags)
        
        with self.assertRaises(KeyError):
            self.inode_entry.set_bit_flag('KeyThatDoesn\'tExists', True)

    def test_is_dir(self):
        self.inode_entry.is_dir = True
        self.assertTrue(self.inode_entry.is_dir)
        self.inode_entry.is_dir = False
        self.assertFalse(self.inode_entry.is_dir)

    def test_is_hidden(self):
        self.inode_entry.is_hidden = True
        self.assertTrue(self.inode_entry.is_hidden)
        self.inode_entry.is_hidden = False
        self.assertFalse(self.inode_entry.is_hidden)

    def test_permissions(self):
        for i in range(256):
            self.inode_entry.permissions = i
            self.assertEqual(self.inode_entry.permissions, i)

        with self.assertRaises(OverflowError):
            self.inode_entry.permissions = 257

    def test_addr(self):
        for i in list(range(256)) + [2 ** (4 * 8)-1]:
            self.inode_entry.addr = i
            self.assertEqual(self.inode_entry.addr, i)

        with self.assertRaises(OverflowError):
            self.inode_entry.addr = 2 ** (4 * 8)

    def test_name(self):
        TEST_NAMES = ['a' * tmp for tmp in range(100)]
        
        for name in TEST_NAMES:
            self.inode_entry.name = name
            self.assertEqual(self.inode_entry.name, name)
        
        with self.assertRaises(ValueError):
            self.inode_entry.name = 'a long name' * 100

    def test_free(self):
        self.inode_entry.addr = 0
        self.assertTrue(self.inode_entry.free)

        for i in list(range(1, 256)) + [2 ** (4 * 8)-1]:
            self.inode_entry.addr = i
            self.assertFalse(self.inode_entry.free, f'Addr is {self.inode_entry.addr}')
        
        with self.assertRaises(AttributeError):
            self.inode_entry.free = True

    def test___str__(self):
        for i in list(range(100)) + [2 ** (4 * 8)-1]:
            self.inode_entry.addr = i
            for name in ['a' * tmp for tmp in range(100)]:
                self.inode_entry.name = name
                self.assertEqual(str(self.inode_entry), f'{i} {name}')
