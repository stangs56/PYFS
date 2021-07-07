import unittest
import io
import os
import logging

from pyfs import PYFS, Inode
from pyfs.constants import DEFAULT_BLOCK_SIZE, BYTE_ORDER, INODE_META_SIZE

from tests.test_common import log_with_debug, log_test_case

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

    @log_test_case
    def test_read_inode(self):
        inode_a = self.pyfs.read_inode(1)

        self.pyfs.block_dev.seek(1*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)
        self.assertEqual(inode_a.addr, 1)
        self.assertEqual(data, inode_a.full_inode_data)

        inode_b = self.pyfs.create_inode()
        self.assertEqual(inode_b.addr, 2)
        inode_b.parent_inode_addr = 1

        self.pyfs.block_dev.seek(2*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)

        if not inode_b.dirty:
            self.assertEqual(data, inode_b.full_inode_data)
        
        self.pyfs.save_all()
        self.pyfs.block_dev.seek(2*DEFAULT_BLOCK_SIZE, 0)
        data = self.pyfs.block_dev.read(DEFAULT_BLOCK_SIZE)

        self.assertEqual(len(data), len(inode_b.full_inode_data))
        self.assertEqual(data, inode_b.full_inode_data)
    
    @log_test_case
    def test_check_fs(self):
        self.assertTrue(self.pyfs.check_fs())

        invalid_size = 0
        self.pyfs.block_dev.seek(0, 0)
        self.pyfs.block_dev.write(invalid_size.to_bytes(2, byteorder=BYTE_ORDER))
        self.assertFalse(self.pyfs.check_fs())
    
    @log_test_case
    def test_create_inode(self):
        NUM_INODES = 200
        for i in range(2, NUM_INODES+1):
            inode = self.pyfs.create_inode()
            self.assertEqual(inode.addr, i)
            inode.parent_inode_addr = i-1

        self.assertEqual(len(self.pyfs.loaded_inodes), NUM_INODES)
    
    @log_test_case
    def test_save_all(self):
        NUM_INODES = 200
        for i in range(2, NUM_INODES+1):
            inode = self.pyfs.create_inode()
            self.assertEqual(inode.addr, i)
            inode.parent_inode_addr = i-1

        loaded_inodes = self.pyfs.loaded_inodes
        self.assertEqual(len(loaded_inodes), NUM_INODES)
        self.pyfs.save_all()
        self.pyfs = PYFS(self.fs)
        self.pyfs.read_root_inode()

        for i in range(2, NUM_INODES+1):
            inode = self.pyfs.read_inode(i)
            self.assertEqual(inode.addr, i)
            self.assertEqual(inode.parent_inode_addr, i-1)
        
        self.assertEqual(len(self.pyfs.loaded_inodes), NUM_INODES)
        self.assertCountEqual(loaded_inodes, self.pyfs.loaded_inodes)
    
    @log_test_case
    def test_write_block(self):
        NUM_BLOCKS = 200
        data = [(tmp.to_bytes(1, byteorder=BYTE_ORDER))*DEFAULT_BLOCK_SIZE for tmp in range(NUM_BLOCKS)]

        for i in range(2, NUM_BLOCKS+1):
            self.pyfs.write_block(i, data[i-2])
        
        self.fs.seek(2*DEFAULT_BLOCK_SIZE, 0)
        for i in range(2, NUM_BLOCKS+1):
            inode = self.fs.read(DEFAULT_BLOCK_SIZE)
            self.assertEqual(inode, data[i-2])
    
    @log_test_case
    def test_write_inode(self):
        NUM_INODE = 200
        for _ in range(2, NUM_INODE+1):
            inode_a = Inode(2, bytes(DEFAULT_BLOCK_SIZE), self.pyfs)
            inode_a.is_dir = False
            inode_a.data = os.urandom(DEFAULT_BLOCK_SIZE-INODE_META_SIZE)
            self.pyfs.write_inode(inode_a)
            inode_b = self.pyfs.read_inode(2, force_read=True)
            self.assertEqual(inode_a, inode_b)

    
