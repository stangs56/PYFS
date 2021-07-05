import logging
import pyfs.pyfs
import pyfs.inode
import shlex

from functools import partial
from pathlib import PurePosixPath

COMMANDS = {}
ALIAS = (('ll', 'ls -l'),)

cwd = PurePosixPath('/')
fs = None
current_inode = None

def set_up_interactive(file_system: 'pyfs.pyfs.PYFS'):
    global fs
    
    fs = file_system
    loadfs()

    commands = COMMANDS
    
    for alias, cmd in ALIAS:
        cmd_split = shlex.split(cmd)
        commands[alias] = partial(COMMANDS[cmd_split[0]], *cmd_split[1:])

    return commands

def register_func(func):
    COMMANDS[func.__name__] = func
    return func

@register_func
def flushfs():
    fs.save_all()

@register_func
def loadfs():
    global fs, current_inode
    fs.read_root_inode()
    current_inode = fs.root_inode

    cd('/')

@register_func
def cat(name):
    global fs, current_inode
    file_addr = current_inode.find_entry(name).addr
    file_inode = fs.read_inode(file_addr)
    print(file_inode.data.decode('utf-8'))

@register_func
def chkfs():
    global fs
    print('Checking Filesystem')
    print(f'Filesystem is {"good" if fs.check_fs() else "bad"}')

@register_func
def mkfs():
    global fs
    if not fs.check_fs():
        fs.create_fs()

@register_func
def mkdir(name):
    global fs, current_inode
    current_inode.make_dir(name)

@register_func
def touch(name):
    global fs, current_inode
    current_inode.make_file(name)

@register_func
def nano(name):
    global fs, current_inode
    content = input()
    file_inode = current_inode.find_entry(name)

    if file_inode is None:
        logging.info('Creating file %s', name)
        current_inode.make_file(name)
        file_inode = current_inode.find_entry(name)

    file_inode = fs.read_inode(file_inode.addr)
    file_inode.data = content.encode('utf-8')


@register_func
def ls(list_long=None):
    global cwd, current_inode
    logging.debug('Current inode is %s', current_inode)

    for cur in current_inode.ls():
        identifier = 'd ' if cur.is_dir else 'f '

        identifier += f'{hex(cur.flags)[2:]} '

        if list_long != '-l':
            identifier = ''

        print(f'{identifier}{cur.name}')

@register_func
def pwd():
    print(cwd.as_posix())

@register_func
def cd(path: str):
    global cwd, fs, current_inode
    old_cwd = cwd
    old_current_inode = current_inode
    path = PurePosixPath(path)
    cwd = cwd / path

    logging.debug(cwd.parts)

    build_path = []
    current_inode = fs.root_inode
    if len(cwd.parts) > 1:
        for dirs in cwd.parts[1:]:
            if dirs == '.':
                continue
            elif dirs == '..':
                if current_inode.parent_inode_addr != 0:
                    current_inode = fs.read_inode(current_inode.parent_inode_addr)
                    build_path = build_path[:-1]
            else:
                tmp = current_inode.find_entry(dirs)

                if tmp is None:
                    print(f'Can\'t find directory {dirs}')
                    cd(old_cwd)
                    return
                
                current_inode = fs.read_inode(tmp.addr)
                build_path.append(dirs)
        cwd = PurePosixPath('/' + '/'.join(build_path))
