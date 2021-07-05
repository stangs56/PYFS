from pyfs.pyfs import PYFS
from pyfs.inode import InodeEntryExists, Inode

import logging

def create_dir_if_not_exists(inode: Inode, name):
    try:
        inode.make_dir(name)
    except InodeEntryExists:
        logging.info('Directory %s already exists', name)


def log_test_case(func, *args, **kargs):
    def tmp(*args, **kargs):
        logging.debug('In %s', func.__name__)
        func(*args, **kargs)
        logging.debug('Leaving %s', func.__name__)
    return tmp

def log_with_debug(func, *args, **kargs):
    def tmp(*args, **kargs):
        old_level = logging.getLogger().level
        logging.getLogger().setLevel(logging.DEBUG)
        func(*args, **kargs)
        logging.getLogger().setLevel(old_level)
    return tmp


def set_up_test_directories(fs: PYFS):
    create_dir_if_not_exists(fs.root_inode, 'etc')
    create_dir_if_not_exists(fs.root_inode, 'bin')
    create_dir_if_not_exists(fs.root_inode, 'home')

    inode_addr = {}
    inode_addr['etc'] = fs.read_inode(fs.root_inode.find_entry('etc').addr)
    inode_addr['etc'] = fs.read_inode(fs.root_inode.find_entry('etc').addr)
    inode_addr['bin'] = fs.read_inode(fs.root_inode.find_entry('bin').addr)
    inode_addr['home'] = fs.read_inode(fs.root_inode.find_entry('home').addr)

    create_dir_if_not_exists(inode_addr['etc'], 'sys')
    create_dir_if_not_exists(inode_addr['etc'], 'network')

    create_dir_if_not_exists(inode_addr['home'], 'nkroft')
    create_dir_if_not_exists(inode_addr['home'], 'swalker')
    create_dir_if_not_exists(inode_addr['home'], 'mandrew')

    create_dir_if_not_exists(inode_addr['etc'], 'X11')

    # Push inode to limit of single
    for idx in range(33):
        create_dir_if_not_exists(inode_addr['bin'], f'tst{idx}')

    fs.save_all()
