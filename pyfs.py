from io import BufferedRandom
import logging

from inode import Inode
from constants import BYTE, DEFAULT_BLOCK_SIZE, INODE_META_SIZE, BYTE_ORDER

logger = logging.getLogger('pyfs')

class PYFS:
    def __init__(self, block_dev: BufferedRandom):
        self.block_dev = block_dev
        self.block_size = DEFAULT_BLOCK_SIZE

        self.root_block = None
        self.root_block_dirty = False

        self.root_inode = None
        self.loaded_inodes = {}
    
    def read_root(self) -> None:
        logger.info('Reading root block')
        self.block_dev.seek(0, 0)
        self.root_block = self.block_dev.read(self.block_size)
        
        self.root_block_dirty = False

    def read_root_inode(self) -> None:
        if self.root_block is None:
            self.read_root()
        
        logger.info('Reading root inode')
        self.root_inode = self.read_inode(1)
    
    def read_inode(self, addr : int, force_read=False) -> Inode:
        logger.debug('Loading inode with addr %s', addr)

        if addr not in self.loaded_inodes or force_read:
            logger.debug('inode %s not loaded, reading from backing storage', addr)
            self.block_dev.seek(addr * self.block_size, 0)
            self.loaded_inodes[addr] = Inode(addr, self.block_dev.read(self.block_size), self)

        return self.loaded_inodes[addr]

    def create_fs(self) -> None:
        logger.info("Creating filesytem...")

        self.block_size = DEFAULT_BLOCK_SIZE

        # Write root block
        logger.debug('Writing Root Block...')
        self.block_dev.seek(0, 0)
        self.block_dev.write(self.block_size.to_bytes(2, byteorder=BYTE_ORDER))
        self.block_dev.write(bytes(self.block_size-2))

        # Write root inode
        logger.debug('Writing Root Inode...')
        self.block_dev.seek(1 * self.block_size, 0)
        tmp = Inode(1, bytes(self.block_size), self)
        tmp.is_dir = True
        self.block_dev.write(tmp.full_inode_data)

        self.block_dev.flush()

        logger.debug('Reading root Inode after creating filesystem...')
        self.read_root_inode()

    def check_fs(self) -> bool:
        logger.debug("Reading root node block size")

        self.block_dev.seek(0, 0)
        self.block_size = int.from_bytes(self.block_dev.read(2), byteorder=BYTE_ORDER)

        if self.block_size < DEFAULT_BLOCK_SIZE:
            logger.warning("Block size is not valid: %s", self.block_size)
            return False
        
        logger.info("Block size is %s", self.block_size)

        self.read_root_inode()

        return True
    
    def create_inode(self) -> Inode:
        self.block_dev.seek(0, 2)
        loc = self.block_dev.tell() // self.block_size

        self.block_dev.write(bytes(self.block_size))

        self.loaded_inodes[loc] = Inode(loc, bytes(self.block_size), self)
        return self.loaded_inodes[loc]
    
    def save_all(self) -> None:
        logger.info('Saving all loaded inodes')
        for addr, inode in self.loaded_inodes.items():
            if inode.dirty:
                logger.debug('inode %s is dirty', addr)
                inode.save()

        if self.root_block_dirty:
            logger.info('Root block is dirty')
            self.write_block(0, self.root_block)
            
    
    def write_block(self, addr : int, data : bytes) -> None:
        logger.debug('Writing block %s to address %s', addr, addr * self.block_size)
        self.block_dev.seek(addr * self.block_size, 0)
        self.block_dev.write(data)
        self.block_dev.flush()

    def write_inode(self, inode: Inode) -> None:
        logger.debug("Writing Inode %s", inode.addr)
        self.write_block(inode.addr, inode.full_inode_data)
        
