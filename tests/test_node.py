import unittest

from pyfs.constants import DEFAULT_BLOCK_SIZE

from tests.test_common import create_dir_if_not_exists, log_with_debug, log_test_case

class TestNode(unittest.TestCase):
    def test_meta(self):
        raise NotImplementedError()

    def test_flags(self):
        raise NotImplementedError()

    def test_set_flags(self):
        raise NotImplementedError()
    
    def test_get_flag(self):
        raise NotImplementedError()
    
    def test_set_meta_bytes(self):
        raise NotImplementedError()

    def test_get_meta_bytes(self):
        raise NotImplementedError()

    def test___repr__(self):
        raise NotImplementedError()
    
    def test___eq__(self):
        raise NotImplementedError()
