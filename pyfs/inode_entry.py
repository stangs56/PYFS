from __future__ import annotations

import logging
import pyfs

from pyfs.constants import BYTE_ORDER, INODE_ENTRY_FLAGS

logger = logging.getLogger("pyfs.inode")

class InodeEntry:
    def __init__(self, data: bytes):
        self._data = data
    
    @property
    def data(self) -> bytes:
        return self._data
    
    @data.setter
    def data(self, value: bytes):
        self._data = value

    @property
    def flags(self) -> int:
        return int.from_bytes(self._data[:1], byteorder=BYTE_ORDER)
    
    @flags.setter
    def flags(self, value: int):
        self._data = value.to_bytes(1, byteorder=BYTE_ORDER) + self._data[1:]

    def get_bit_flag(self, field) -> bool:
        return self.flags & INODE_ENTRY_FLAGS[field]
    
    def set_bit_flag(self, field, value: bool):
        if value:
            self.flags = self.flags | INODE_ENTRY_FLAGS[field]
        else:
            self.flags = self.flags & ~INODE_ENTRY_FLAGS[field]

    @property
    def is_dir(self) -> bool:
        return self.get_bit_flag('is_directory')

    @is_dir.setter
    def is_dir(self, value: bool):
        self.set_bit_flag('is_directory', value)
    
    @property
    def is_hidden(self) -> bool:
        return self.get_bit_flag('is_hidden')

    @is_hidden.setter
    def is_hidden(self, value: bool):
        self.set_bit_flag('is_hidden', value)

    @property
    def permissions(self) -> int:
        return int.from_bytes(self._data[1:2], byteorder=BYTE_ORDER)
    
    @permissions.setter
    def permissions(self, value: int):
        self._data = self._data[:1] + value.to_bytes(1, byteorder=BYTE_ORDER) + self._data[2:6]

    @property
    def addr(self) -> int:
        return int.from_bytes(self._data[2:6], byteorder=BYTE_ORDER)
    
    @addr.setter
    def addr(self, value: int):
        self._data = self._data[:2] + value.to_bytes(4, byteorder=BYTE_ORDER) + self._data[6:]

    @property
    def name(self) -> str:
        return self._data[6:].decode('utf-8').rstrip('\0')
    
    @name.setter
    def name(self, value: str):
        value = value.encode('utf-8')

        if len(value) > 122:
            raise ValueError('Name must be able to be encoded in under 122 bytes')
        
        value = value + bytes(122 - len(value))
        self._data = self._data[:6] + value

    @property
    def free(self):
        return (self.addr == 0)
    
    def __str__(self):
        return f'{self.addr} {self.name}'
