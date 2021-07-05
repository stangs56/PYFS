from __future__ import annotations

import logging
import pyfs

from constants import BYTE, INODE_META_SIZE, BYTE_ORDER, INODE_FLAGS
from inode_entry import InodeEntry
from node import Node

logger = logging.getLogger("pyfs.inode")

class Inode(Node):
    def __init__(self, addr: int, data: bytes, fs: 'pyfs.PYFS'):
        self.meta_flag_locs = INODE_FLAGS
        super().__init__(addr, data, fs)
    
    @property
    def children(self) -> 'list[InodeEntry]':
        if self.is_dir and self._children is not None:
            return self._children
        elif self.is_dir:
            self._children = [InodeEntry(self._data[i:i+INODE_META_SIZE]) for i in range(INODE_META_SIZE, len(self._data), INODE_META_SIZE)]
            logger.debug("files in inode: %s", len([a for a in self._children if not a.free]))
            return self._children
        else:
            return []

    @property
    def is_dir(self) -> bool:
        return self.get_flag('is_directory')
    
    @is_dir.setter
    def is_dir(self, value: bool):
        self.set_flags('is_directory', value)

    @property
    def contains_data(self) -> bool:
        return self.get_flag('contains_data')
    
    @contains_data.setter
    def contains_data(self, value: bool):
        self.set_flags('contains_data', value)

    @property
    def parent_inode_addr(self) -> int:
        return self.get_meta_bytes(2, 4)

    @parent_inode_addr.setter
    def parent_inode_addr(self, value: int):
        logger.debug('Inode %s parent_inode_addr set to %s', self.addr, value)

        self.set_meta_bytes(value, 2, 4)
    
    @property
    def next_inode_addr(self) -> int:
        return self.get_meta_bytes(6, 4)

    @next_inode_addr.setter
    def next_inode_addr(self, value: int):
        logger.debug('Inode %s next_inode_addr set to %s', self.addr, value)

        self.set_meta_bytes(value, 6, 4)
    
    @property
    def data_size(self) -> int:
        return self.get_meta_bytes(12, 2)
    
    @data_size.setter
    def data_size(self, value):
        logger.debug('Inode %s data_size set to %s', self.addr, value)

        self.set_meta_bytes(value, 12, 2)

    @property
    def full_inode_data(self) -> bytes:
        return self.meta + self.data
    
    @property
    def data(self) -> bytes:
        if self.is_dir:
            tmp = bytes()

            for child in self.children:
                # inode_logger.debug(child.data)
                tmp += child.data
            
            return tmp
        else:
            return self._data[INODE_META_SIZE:INODE_META_SIZE+self.data_size]

    @data.setter
    def data(self, value : bytes):
        if not self.is_dir:
            if len(value) > self.fs.block_size - INODE_META_SIZE:
                raise RuntimeError('Data is too big to fit in single Inode')
            self.dirty = True
            self.contains_data = True
            self.data_size = len(value)
            self._data = self._data[:INODE_META_SIZE] + value + self._data[INODE_META_SIZE+len(value):]
        else:
            raise RuntimeError('Inode is a directory')

    def ls(self, show_hidden=False) -> 'list[InodeEntry]':
        logger.debug('Inode %s has children %s', self.addr, [a.addr for a in self.children])

        next_inode_ls = []
        if self.next_inode_addr != 0:
            logger.debug('Inode %s loading Inode %s for extra entries', self.addr, self.next_inode_addr)
            next_inode_ls = self.fs.read_inode(self.next_inode_addr).ls(show_hidden=show_hidden)

        return [a for a in self.children if not a.free and (not a.is_hidden or show_hidden)] + next_inode_ls
    
    def find_entry(self, name) -> InodeEntry:
        for a in self.ls():
            if a.name == name:
                logger.debug('Matched %s to %s', a, name)
                return a
        return None
    
    def add_inode_entry(self, name, child: 'Inode'):
        logger.debug("Inode %s Adding Inode Entry...", self.addr)
        self.dirty = True
        for ie in self.children:
            if ie.free:
                logger.debug('Inode %s added entry for Inode %s', self.addr, child.addr)
                ie.addr = child.addr
                ie.is_dir = child.is_dir
                ie.name = name
                break
        else:
            if self.next_inode_addr == 0:
                logger.info('Inode %s Adding Inode to store extra entries', self.addr)
                tmp = self.fs.create_inode()
                tmp.is_dir = True
                tmp.parent_inode_addr = self.addr
                self.next_inode_addr = tmp.addr
            
            self.fs.read_inode(self.next_inode_addr).add_inode_entry(name, child)
        
        self.save()
    
    def check_if_exists(self, name):
        for child in self.ls():
            if name == child.name:
                logger.info('Inode %s name %s already exists', self.addr, name)
                raise InodeEntryExists()

    def create_child_inode(self, name, is_dir):
        self.check_if_exists(name)
        tmp = self.fs.create_inode()
        tmp.is_dir = is_dir
        tmp.parent_inode_addr = self.addr
        tmp.save()

        self.dirty = True
        self.add_inode_entry(name, tmp)

    def make_dir(self, name):
        logger.info("Inode %s Creating directory: %s", self.addr, name)
        self.create_child_inode(name, True)
    
    def make_file(self, name):
        logger.info("Inode %s Creating file: %s", self.addr, name)
        self.create_child_inode(name, False)

    def save(self):
        logger.debug("Saving Inode %s", self.addr)
        logger.debug("Inode %s dirty bit is set to %s", self.addr, self.dirty)
        self.fs.write_inode(self)
        self.dirty = False
    
    def __repr__(self) -> str:
        return f"Inode {self.addr}: contains_data: {self.contains_data} is_dirty: {self.dirty} parent: {self.parent_inode_addr} next: {self.next_inode_addr}"

class InodeError(Exception):
    pass

class InodeEntryExists(InodeError):
    pass

class OutOfInodeError(InodeError):
    pass