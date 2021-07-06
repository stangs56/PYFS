from __future__ import annotations

import logging
import pyfs.pyfs
from pyfs.constants import INODE_META_SIZE, BYTE_ORDER, INODE_FLAGS
from pyfs.inode_entry import InodeEntry

logger = logging.getLogger("pyfs.node")

class Node:
    def __init__(self, addr: int, data: bytes, fs: 'pyfs.pyfs.PYFS'):
        #self.meta = data[:INODE_META_SIZE]
        logger.debug("Meta data for Node %s: %s", addr, data[:INODE_META_SIZE])

        self._data = data
        self._children = None
        self.dirty = False

        self.addr = addr
        self.fs = fs

        self.meta_flag_locs = []
    
    @property
    def meta(self) -> bytes:
        return self._data[:INODE_META_SIZE]
    
    @meta.setter
    def meta(self, value):
        self._data = value + self._data[INODE_META_SIZE:]

    @property
    def flags(self) -> int:
        return int.from_bytes(self.meta[:2], byteorder=BYTE_ORDER)
    
    @flags.setter
    def flags(self, value: int):
        logger.debug('Node %s flags set to %s', self.addr, value)

        self.set_meta_bytes(value, 0, 2)

    def set_flags(self, property, value :bool):
        self.dirty = True
        logger.debug('node %s %s set to %s', self.addr, property, value)

        if value:
            self.flags = self.flags | self.meta_flag_locs[property]
        else:
            self.flags = self.flags & ~self.meta_flag_locs[property]
    
    def get_flag(self, property) -> bool:
        return bool(self.flags & self.meta_flag_locs[property])

    def set_meta_bytes(self, value, start_pos, size):
        self.dirty = True
        self.meta = self.meta[:start_pos] + value.to_bytes(size, byteorder=BYTE_ORDER) + self.meta[start_pos+size:]
    
    def get_meta_bytes(self, start_pos, size, type=int):
        return type.from_bytes(self.meta[start_pos:start_pos+size], byteorder=BYTE_ORDER)
    
    def __repr__(self) -> str:
        return f"Node {self.addr}: Meta - {self.meta} Data - {self._data}"

    def __eq__(self, other : Node):
        logging.debug('Comparing equality of Nodes %s and %s', self.addr, other.addr)
        if self._data != other._data:
            logging.debug('self data:  %s', self._data)
            logging.debug('other data: %s', other._data)
            return False
        else:
            return True 
