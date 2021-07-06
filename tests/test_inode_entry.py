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

class TestInodeEntry(unittest.TestCase):
    def test_data(self):
        raise NotImplementedError()

    def test_flags(self):
        raise NotImplementedError()

    def test_get_bit_flag(self):
        raise NotImplementedError()

    def test_set_bit_flag(self):
        raise NotImplementedError()

    def test_is_dir(self):
        raise NotImplementedError()

    def test_is_hidden(self):
        raise NotImplementedError()

    def test_permissions(self):
        raise NotImplementedError()

    def test_addr(self):
        raise NotImplementedError()

    def test_name(self):
        raise NotImplementedError()

    def test_free(self):
        raise NotImplementedError()

    def test___str__(self):
        raise NotImplementedError()