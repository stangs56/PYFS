
class InodeError(Exception):
    pass

class InodeEntryExists(InodeError):
    pass

class OutOfInodeError(InodeError):
    pass
