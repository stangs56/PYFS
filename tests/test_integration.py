import inode_entry
from typing import List
from inode import Inode
import unittest
import io
import logging

from pyfs import PYFS
from inode import InodeEntryExists
from constants import DEFAULT_BLOCK_SIZE

from tests.test_common import create_dir_if_not_exists, log_with_debug, log_test_case

logging.basicConfig(filename="test_pyfs.log", level=logging.WARNING)

class TestPYFS(unittest.TestCase):
    @log_test_case
    def setUp(self):
        self.fs = io.BytesIO()
        self.pyfs = PYFS(self.fs)
        self.pyfs.create_fs()
    
    def assertChildInodes(self, inode : Inode = None, inode_names : List[str] = None) -> None:
        if inode is None:
            inode = self.pyfs.root_inode
        if inode_names is None:
            inode_names = []
        dirs = [tmp.name for tmp in inode.ls()]

        #checks that the same number of each element are present
        self.assertCountEqual(dirs, inode_names)
    
    @log_test_case
    def test_integration(self):
        #assert no directories exist in the root directory
        self.assertChildInodes()

        create_dir_if_not_exists(self.pyfs.root_inode, 'etc')
        self.assertChildInodes(inode_names=['etc'])

        create_dir_if_not_exists(self.pyfs.root_inode, 'home')
        self.assertChildInodes(inode_names=['etc', 'home'])

        create_dir_if_not_exists(self.pyfs.root_inode, 'bin')
        self.assertChildInodes(inode_names=['etc', 'home', 'bin'])

        inode_addr = {}
        inode_addr['etc'] = self.pyfs.read_inode(self.pyfs.root_inode.find_entry('etc').addr)
        self.assertChildInodes(inode_addr['etc'])

        inode_addr['bin'] = self.pyfs.read_inode(self.pyfs.root_inode.find_entry('bin').addr)
        self.assertChildInodes(inode_addr['bin'])

        inode_addr['home'] = self.pyfs.read_inode(self.pyfs.root_inode.find_entry('home').addr)
        self.assertChildInodes(inode_addr['home'])

        create_dir_if_not_exists(inode_addr['etc'], 'sys')
        self.assertChildInodes(inode_addr['etc'], ['sys'])

        create_dir_if_not_exists(inode_addr['etc'], 'network')
        self.assertChildInodes(inode_addr['etc'], ['sys', 'network'])

        create_dir_if_not_exists(inode_addr['home'], 'nkroft')
        self.assertChildInodes(inode_addr['home'], ['nkroft'])

        create_dir_if_not_exists(inode_addr['home'], 'swalker')
        self.assertChildInodes(inode_addr['home'], ['nkroft', 'swalker'])

        create_dir_if_not_exists(inode_addr['home'], 'mandrew')
        self.assertChildInodes(inode_addr['home'], ['nkroft', 'swalker', 'mandrew'])

        create_dir_if_not_exists(inode_addr['etc'], 'X11')
        self.assertChildInodes(inode_addr['etc'], ['sys', 'network', 'X11'])

        #directory that already exists should not be added
        create_dir_if_not_exists(inode_addr['etc'], 'network')
        self.assertRaises(InodeEntryExists, inode_addr['etc'].make_dir, 'network')
        
        #verify all directories are as expected
        self.assertChildInodes(inode_addr['etc'], ['sys', 'network', 'X11'])
        self.assertChildInodes(inode_addr['home'], ['nkroft', 'swalker', 'mandrew'])
        self.assertChildInodes(inode_addr['bin'])
        self.assertChildInodes(inode_names=['etc', 'home', 'bin'])
    
    @log_test_case
    def test_directory_creation(self):
        #assert no directories exist in the root directory
        self.assertChildInodes()

        create_dir_if_not_exists(self.pyfs.root_inode, 'etc')
        self.assertChildInodes(inode_names=['etc'])

        create_dir_if_not_exists(self.pyfs.root_inode, 'home')
        self.assertChildInodes(inode_names=['etc', 'home'])

        create_dir_if_not_exists(self.pyfs.root_inode, 'bin')
        self.assertChildInodes(inode_names=['etc', 'home', 'bin'])
    
    @log_test_case
    def test_file_creation(self):
        #assert no directories exist in the root directory
        self.assertChildInodes()

        file_inode = self.pyfs.root_inode.find_entry('tst')
        self.assertIsNone(file_inode)

        self.pyfs.root_inode.make_file('tst')
        self.assertChildInodes(inode_names=['tst'])
        self.assertFalse(self.pyfs.root_inode.find_entry('tst').is_dir)

        file_inode_entry = self.pyfs.root_inode.find_entry('tst')
        self.assertIsNotNone(file_inode_entry)
        self.assertEqual(file_inode_entry.addr, 2)
        self.assertFalse(file_inode_entry.is_dir)
        self.assertFalse(file_inode_entry.is_hidden)
        self.assertFalse(file_inode_entry.free)

        file_inode = self.pyfs.read_inode(file_inode_entry.addr)
        self.assertIsNotNone(file_inode)
        self.assertEqual(file_inode.addr, 2)
        self.assertFalse(file_inode.is_dir)
        self.assertFalse(file_inode.contains_data)

        for file_str in ('hi this are words', '', '\n\n\n\n', '\x00hi\x00'):
            file_inode = self.pyfs.read_inode(file_inode_entry.addr)
            self.assertIsNotNone(file_inode)
            self.assertFalse(file_inode.is_dir)

            file_data = file_str.encode('utf-8')
            file_inode.data = file_data

            self.assertEqual(file_inode.addr, 2)
            self.assertEqual(file_inode.data, file_data)
            self.assertEqual(file_inode.data_size, len(file_data))
            self.assertEqual(file_inode.data.decode('utf-8'), file_str)
            self.assertTrue(file_inode.contains_data)
            self.assertTrue(file_inode.dirty)

            #write out inodes and then force the reload of the file inode
            self.pyfs.save_all()
            file_inode_new = self.pyfs.read_inode(file_inode_entry.addr, force_read=True)

            self.assertIsNot(file_inode, file_inode_new)
            self.assertEqual(file_inode_new.data, file_data)
            self.assertEqual(file_inode_new.data.decode('utf-8'), file_str)
            self.assertEqual(file_inode, file_inode_new)
