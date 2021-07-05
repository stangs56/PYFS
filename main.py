import argparse
from io import IncrementalNewlineDecoder
import logging
import os
import code
import shlex

from pyfs.pyfs import PYFS
from pyfs.inode import InodeEntryExists, Inode
from interactive_utils import set_up_interactive

#set up logging levels for all the different loggers
logging.basicConfig(filename="pyfs.log", level=logging.DEBUG)
logging.getLogger('pyfs').setLevel(logging.DEBUG)
#logging.getLogger('pyfs.inode').setLevel(logging.INFO)

def touchopen(filename, *args, **kwargs):
    # Open the file in R/W and create if it doesn't exist. *Don't* pass O_TRUNC
    fd = os.open(filename, os.O_RDWR | os.O_CREAT | os.O_BINARY)

    # Encapsulate the low-level file descriptor in a python file object
    return os.fdopen(fd, *args, **kwargs)

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--interactive', '-i', action='store_true')
    
    parser.add_argument("file")
    
    args = parser.parse_args()

    filename = args.file
    with touchopen(filename, "w+b") as f:
        logging.debug('filestream is %s', f)
        fs = PYFS(f)

        if args.interactive:
            commands = set_up_interactive(fs)

            try:
                while (entered := input('>> ')) != 'exit':
                    if entered.strip() == '':
                        continue

                    split = shlex.split(entered)
                    try:
                        commands[split[0]](*split[1:])
                    except KeyError:
                        print('Unknown Command')
                    except TypeError as e:
                        print(e.args[0])

            except KeyboardInterrupt:
                pass
            
            print('Exiting Shell')
            fs.save_all()
            return

        if not fs.check_fs():
            fs.create_fs()

        #set_up_test_directories(fs)
        
        for a in fs.root_inode.ls():
            print(a)
            name = a.name
            a = fs.read_inode(a.addr)
            
            for b in a.ls():
                print('  ', b)
        

if __name__ == "__main__":
    main()