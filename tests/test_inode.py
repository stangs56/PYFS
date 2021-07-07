import unittest

from unittest.mock import Mock, MagicMock

from pyfs import Inode, InodeEntry
from pyfs.constants import DEFAULT_BLOCK_SIZE, INODE_META_SIZE, INODE_ENTRY_SIZE, BYTE_ORDER

from tests.test_common import create_dir_if_not_exists, log_with_debug, log_test_case

class TestInode(unittest.TestCase):
    def setUp(self) -> None:
        self.fs_mock = Mock()
        self.fs_mock.block_size = DEFAULT_BLOCK_SIZE
        self.inode = Inode(0, bytes(DEFAULT_BLOCK_SIZE), self.fs_mock)

    def test_children(self):
        self.inode.is_dir = True
        self.assertEqual(len(self.inode.children), 31)

        self.inode.is_dir = False
        self.assertEqual(len(self.inode.children), 0)

        self.inode.contains_data = False
        self.assertEqual(len(self.inode.children), 0)

        entry = InodeEntry(bytes(128))
        entry.addr = 1234
        entry.is_dir = True
        entry.is_hidden = True
        entry.name = 'tst_hi'
        entry.permissions = 0xff

        self.setUp()
        self.inode.is_dir = True
        self.inode._data = self.inode._data[:INODE_META_SIZE] + entry.data + self.inode._data[INODE_META_SIZE+INODE_ENTRY_SIZE:]
        entry2 = self.inode.children[0]

        self.assertEqual(entry, entry2)

    def test_is_dir(self):
        self.inode.is_dir = True
        self.assertTrue(self.inode.is_dir)
        self.inode.is_dir = False
        self.assertFalse(self.inode.is_dir)

    def test_contains_data(self):
        self.inode.contains_data = True
        self.assertTrue(self.inode.contains_data)
        self.inode.contains_data = False
        self.assertFalse(self.inode.contains_data)

    def test_parent_inode_addr(self):
        for i in list(range(256)) + [2 ** (4 * 8)-1]:
            self.inode.parent_inode_addr = i
            self.assertEqual(self.inode.parent_inode_addr, i)

        with self.assertRaises(OverflowError):
            self.inode.parent_inode_addr = 2 ** (4 * 8)

    def test_next_inode_addr(self):
        for i in list(range(256)) + [2 ** (4 * 8)-1]:
            self.inode.next_inode_addr = i
            self.assertEqual(self.inode.next_inode_addr, i)

        with self.assertRaises(OverflowError):
            self.inode.next_inode_addr = 2 ** (4 * 8)
    
    def test_data_size(self):
        for i in list(range(256)) + [2 ** (2 * 8)-1]:
            self.inode.data_size = i
            self.assertEqual(self.inode.data_size, i)

        with self.assertRaises(OverflowError):
            self.inode.data_size = 2 ** (2 * 8)
    
    def test_full_inode_data(self):
        self.assertEqual(self.inode.full_inode_data, bytes(DEFAULT_BLOCK_SIZE))

        self.inode.meta = b'\x7f' + b'\xff'*(INODE_META_SIZE-1)
        self.assertFalse(self.inode.is_dir)
        self.assertEqual(self.inode.full_inode_data, b'\x7f' + b'\xff'*(INODE_META_SIZE-1) + bytes(DEFAULT_BLOCK_SIZE-INODE_META_SIZE))

        self.inode.meta = b'\xff'*INODE_META_SIZE
        self.assertTrue(self.inode.is_dir)
        self.assertEqual(self.inode.full_inode_data, b'\xff'*INODE_META_SIZE + bytes(DEFAULT_BLOCK_SIZE-INODE_META_SIZE))

        self.inode.is_dir = True

        for i in range(31):
            tmp = Mock(['data'])
            tmp.data = b'\xff'*INODE_META_SIZE

            self.inode.children[i] = tmp
            self.assertEqual(self.inode.children[i].data, b'\xff'*INODE_META_SIZE)

        self.assertEqual(self.inode.full_inode_data, b'\xff'*DEFAULT_BLOCK_SIZE)

    def test_data(self):
        self.inode.is_dir = False
        for base_data in range(1, 256, 20):
            for data_length in range(1, DEFAULT_BLOCK_SIZE-INODE_META_SIZE, 20):
                data = base_data.to_bytes(1, byteorder=BYTE_ORDER)*data_length
                self.inode.data = data
                self.assertEqual(self.inode.data, data)
        
        self.inode.is_dir = True
        with self.assertRaises(RuntimeError):
            self.inode.data = 'aaaa'
        
        with self.assertRaises(RuntimeError):
            tmp = self.inode.data

    def test_ls(self):
        self.inode.is_dir = True
        raise NotImplementedError()

    def test_find_entry(self):
        raise NotImplementedError()

    def test_add_inode_entry(self):
        raise NotImplementedError()

    def test_check_if_exists(self):
        raise NotImplementedError()

    def test_create_child_inode(self):
        raise NotImplementedError()
    
    def test_make_dir(self):
        raise NotImplementedError()

    def test_make_file(self):
        raise NotImplementedError()

    def test_save(self):
        raise NotImplementedError()
        
    def test__repr__(self):
        raise NotImplementedError()
