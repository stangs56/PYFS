from sys import implementation
from typing import List
from pyfs.inode import Inode
import unittest
import io
import logging

from pyfs.pyfs import PYFS
from pyfs.inode import InodeEntryExists
from pyfs.inode_entry import InodeEntry
from pyfs.constants import DEFAULT_BLOCK_SIZE

from tests.test_common import create_dir_if_not_exists, log_with_debug, log_test_case

class TestInode(unittest.TestCase):
    def test_children(self):
        raise NotImplementedError()

    def test_is_dir(self):
        raise NotImplementedError()

    def test_contains_data(self):
        raise NotImplementedError()

    def test_parent_inode_addr(self):
        raise NotImplementedError()

    def test_next_inode_addr(self):
        raise NotImplementedError()
    
    def test_data_size(self):
        raise NotImplementedError()
    
    def test_full_inode_data(self):
        raise NotImplementedError()

    def test_data(self):
        raise NotImplementedError()

    def test_ls(self):
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