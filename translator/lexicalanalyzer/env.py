from .idtable import IdTable
from .idtable import IdTableFactory


class Env:
    '''Represents the tree structure of the scope name tables'''

    def __init__(self):
        self.root = None
        self.factory = IdTableFactory()

    def insertnewscope(self, ptr):
        '''Create a new table of names for the current scope as new child of "ptr" table
        and return pointer to the new table of names'''
        newidtable = self.factory.createtable(ptr)
        if self.root is None:
            self.root = newidtable
        else:
            ptr.childs.append(newidtable)
        return newidtable

    def searchelem(self, ptr, id):
        '''function returns the description of the identifier in the current scope, if not,
         then continue to search in the scope level higher'''
        if ptr is None:
            return -1
        if ptr.getid(id) is not None:
            return ptr.getid(id)
        return self.searchelem(ptr.prev, id)

    def __eq__(self, other):
        if not isinstance(other, Env):
            raise Exception("comparable object isn't Env")
        return self.root == other.root

    def printenv(self):
        '''Output of ast tree'''
        def search(ptr: IdTable, level):
            print(str(level) + ':' + '|' + level * ' ' + '├-' + str(ptr))
            if ptr.childs:
                for i in ptr.childs:
                    search(i, level + 1)

        level = 0
        search(self.root, level)
        print()
