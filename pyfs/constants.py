'''Constants for the pyfs package'''

BYTE = 1
KB = 1024 * BYTE
MB = 1024 * KB
GB = 1024 * MB
TB = 1024 * GB
DEFAULT_BLOCK_SIZE = 4 * KB

INODE_META_SIZE = 128

BYTE_ORDER = 'big'

INODE_ENTRY_FLAGS = {'is_directory' : 1 << 7,
                     'is_hidden' : 1 << 6,
                    }

INODE_FLAGS = {'is_directory' : 1 << 15,
               'contains_data' : 1 << 14}
