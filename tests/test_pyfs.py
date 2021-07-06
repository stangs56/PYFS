import unittest
import io
import logging

from pyfs import PYFS
from pyfs.constants import DEFAULT_BLOCK_SIZE, BYTE_ORDER

from tests.test_common import log_with_debug, log_test_case

logging.basicConfig(filename="test_pyfs.log", level=logging.WARNING)

class TestPYFS(unittest.TestCase):
    @log_test_case
    def setUp(self):
        self.fs = io.BytesIO()
        self.pyfs = PYFS(self.fs)
        self.pyfs.create_fs()
    
    @log_test_case
    def test_create_fs(self):
        self.assertIsNotNone(self.pyfs.root_block)
        self.assertIsNotNone(self.pyfs.root_inode)
        self.assertEqual(self.pyfs.block_size, DEFAULT_BLOCK_SIZE)

    @log_test_case
    def test_read_root(self):
        self.pyfs.root_block = None
        self.assertIsNone(self.pyfs.root_block)
        self.pyfs.read_root()
        self.assertIsNotNone(self.pyfs.root_block)
    
    @log_test_case
    def test_read_root_inode(self):
        self.pyfs.root_inode = None
        self.assertIsNone(self.pyfs.root_inode)
        self.pyfs.read_root_inode()
        self.assertIsNotNone(self.pyfs.root_inode)

    @log_with_debug
    @log_test_case
    def test_read_inode(self):
        a = self.pyfs.read_inode(1)

        self.pyfs.block_dev.seek(1*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)
        self.assertEqual(a.addr, 1)
        self.assertEqual(data, a.full_inode_data)

        b = self.pyfs.create_inode()
        self.assertEqual(b.addr, 2)
        b.parent_inode_addr = 1

        self.pyfs.block_dev.seek(2*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)

        if not b.dirty:
            self.assertEqual(data, b.full_inode_data)
        
        self.pyfs.save_all()
        self.pyfs.block_dev.seek(2*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)

        self.assertEqual(len(data), len(b.full_inode_data))
        self.assertEqual(data, b.full_inode_data)
    
    @log_test_case
    def test_check_fs(self):
        self.assertTrue(self.pyfs.check_fs())

        invalid_size = 0
        self.pyfs.block_dev.seek(0, 0)
        self.pyfs.block_dev.write(invalid_size.to_bytes(2, byteorder=BYTE_ORDER))
        self.assertFalse(self.pyfs.check_fs())
    
    @unittest.expectedFailure
    def test_create_inode(self):
        self.assertFalse(True)
    
    @unittest.expectedFailure
    def test_save_all(self):
        self.assertFalse(True)
    
    @unittest.expectedFailure
    def test_write_block(self):
        self.assertFalse(True)
    
    @unittest.expectedFailure
    def test_write_inode(self):
        self.assertFalse(True)
    
