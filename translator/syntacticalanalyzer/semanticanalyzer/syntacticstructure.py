from __future__ import annotations
from ...lexicalanalyzer.env import Env
from ...lexicalanalyzer.idtable import IdTable
from ..recognizer.syntacticaltree import SyntacticalTree
from ..recognizer.syntacticaltree import Node
from ..recognizer.rule import Rule


class NodeStruct:
    def __init__(self, isNonterminal: bool, name: str, value: str = '', prev: NodeStruct = None) -> None:
        self.name = name
        self.value = value
        self.idtable = None
        self.isNonterminal = isNonterminal
        self.prev: NodeStruct = prev
        self.childs: list(NodeStruct) = []

    def __str__(self):
        nonterm = "Nonterminal"
        if self.isNonterminal == False:
            nonterm = "Terminal"
        res = '[' + nonterm + ';' + self.name + ';' + self.value + ']'
        return res

    def __repr__(self):
        nonterm = "Nonterminal"
        if self.isNonterminal == False:
            nonterm = "Terminal"
        res = '[' + nonterm + ';' + self.name + ';' + self.value + ']'
        return res

    @property
    def me(self) -> NodeStruct:
        for i in range(len(self.prev.childs)):
            if self == self.prev.childs[i]:
                return self.prev.childs[i]

    @me.setter
    def me(self, newNode) -> None:
        if self.prev == None:
            self.childs = newNode.childs
            self.value = newNode.value
            self.isNonterminal = newNode.isNonterminal
            self.name = newNode.name
        else:
            for i in range(len(self.prev.childs)):
                if self == self.prev.childs[i]:
                    self.prev.childs[i].childs = newNode.childs
                    self.prev.childs[i].value = newNode.value
                    self.prev.childs[i].isNonterminal = newNode.isNonterminal
                    self.prev.childs[i].name = newNode.name
                    break

    @me.deleter
    def me(self):
        del self


class SyntacticsStructure:
    def __init__(self, stree: SyntacticalTree):
        self.uselessterms = ["public", "static", "void", "main", "(", "String[]", "args", ")", "{", "}", "class", ",",
                             "if",
                             "System.out.print","\'", "for", "while", "\"", ";", "do"]
        self.operations = ['+', '-', '*', '/', '%', '>', '<', '>=', '<=', '==', '!=', '&&', '||', '=']
        self.unaroperations = ['!', '++', '--']
        self.root = self.__copytree(stree)
        self.__reformattree(self.root)
        self.__fixtree(self.root)

    def __isoperation(self, ptr: NodeStruct) -> bool:
        '''Check if the node has signed descendants'''
        if ptr.name in ['STRING']:
            return False
        """if self.__havealonechild(ptr):
            if ptr.childs[0].name in (self.operations + self.unaroperations):
                return True"""
        if True:
            if len(ptr.childs) == 3 and ptr.childs[1].name in self.operations \
                    and ptr.childs[1].childs == [] :
                return True
            elif len(ptr.childs) == 2 and \
                    (ptr.childs[0].name in self.unaroperations and ptr.childs[0].childs == [] or
                     ptr.childs[1].name in self.unaroperations and ptr.childs[1].childs == []):
                return True
        return False

    def __deleteoperationterm(self, ptr: NodeStruct) -> None:
        '''Delete operation term in Node'''
        """        for i in ptr.childs:
            if i.name in (self.operations + self.unaroperations):
                ptr.me.name = i.name
                ptr.me.isNonterminal = i.isNonterminal
                ptr.childs.remove(i)
                break"""
        i = ptr.childs[1]
        if len(ptr.childs) == 3 and ptr.childs[1].name in self.operations:
            i = ptr.childs[1]
        elif len(ptr.childs) == 2 :
            if ptr.childs[0].name in self.unaroperations:
                i = ptr.childs[0]
            elif ptr.childs[1].name in self.unaroperations:
                i = ptr.childs[1]
        ptr.me.name = i.name
        ptr.me.isNonterminal = i.isNonterminal
        ptr.childs.remove(i)
        """"""

    def __haveuselessterm(self, ptr: NodeStruct):
        '''checks the tree for useless symbols'''
        res = False
        for i in ptr.childs:
            if i.name in self.uselessterms:
                res = True
                break
        return res

    def __deleteuslessterm(self, ptr: NodeStruct) -> None:
        '''Delete useless terminal symbol'''
        for j in range(len(ptr.prev.childs)):
            if ptr.prev.childs[j] == ptr:
                for i in ptr.childs:
                    if i.name in self.uselessterms:
                        ptr.prev.childs[j].childs.remove(i)
                        break
                break

    def __checkcomplete(self) -> bool:
        '''checks the tree for nonterminal symbols step 1'''

        def _search(ptr: NodeStruct):
            if ptr.isNonterminal:
                return False
            if ptr.childs:
                for i in ptr.childs:
                    return _search(i)
            return True

        return _search(self.root)

    def __havealonechild(self, ptr: NodeStruct) -> bool:
        '''Does a node have a single descendant node'''
        return len(ptr.childs) == 1

    def __getoperationchildcount(self, ptr: NodeStruct) -> int:
        '''Does a node have a single operation descendant node'''
        opcount = 0
        for i in ptr.childs:
            if i.name in self.operations + self.unaroperations:
                opcount += 1
        return opcount

    def __getoperationindex(self, ptr: NodeStruct) -> int:
        '''Does a node have a single operation descendant node'''
        for i, t in enumerate(ptr.childs):
            if t.name in self.operations + self.unaroperations:
                return i
        return -1

    def __havenonterminalchilds(self, ptr: NodeStruct) -> bool:
        '''check non terminal childs of ptr Node'''

        def _search(ptr: NodeStruct):
            if ptr.isNonterminal:
                return False
            if ptr.childs:
                for i in ptr.childs:
                    if _search(i) == True:
                        return False
            return True

        return _search(ptr)

    def __replace_node(self, parent: NodeStruct, newNode: NodeStruct) -> None:
        '''Replacing a node with a new node'''
        parent.me = newNode

    def __reformattree(self, ptr: NodeStruct) -> None:
        '''Modification of algorithm for converting an output tree into an operation tree https://studopedia.su/14_133217_derevo-razbora-preobrazovanie-dereva-razbora-v-derevo-operatsiy.html'''
        #self.printast()
        while not self.__checkcomplete():  # step 1
            while True:
                lastnode = self.__getlastnonterm(ptr)  # step 2
                """if lastnode.name == 'NUMBER':
                    print()"""
                if self.__havealonechild(lastnode) \
                    and (lastnode.name not in ["IDENTIFICATOR", "INTEGER NUMBER", "STRING", "BOOL VALUE", "OUTPUT FUNCTION", "PROGRAMM"]):  # step3
                    lastnode.me = lastnode.childs[0]
                    self.__reformattree(ptr)  # return to step1
                elif self.__haveuselessterm(lastnode):  # step 4
                    self.__deleteuslessterm(lastnode)
                elif self.__isoperation(lastnode):  # step 5
                    self.__deleteoperationterm(lastnode)
                    self.__reformattree(ptr)
                elif lastnode.isNonterminal:
                    if (lastnode.name, lastnode.prev.name) in [
                        ("IDENTIFICATOR", "IDENTIFICATOR"),
                        ("IDENTIFICATOR", "DIGIT_ID"),
                        ("DIGIT_ID", "IDENTIFICATOR"),
                        ("DIGIT_ID", "DIGIT_ID"),
                        ("STRING", "STRING"),
                        ("INTEGER NUMBER", "INTEGER NUMBER"),
                        ("INTEGER NUMBER", "SIGNED NUM"),
                        ("REAL NUMBER", "SIGNED NUM"),
                    ]:
                        if (lastnode.name, lastnode.prev.name) in [
                            ("INTEGER NUMBER", "SIGNED NUM"),
                            ("REAL NUMBER", "SIGNED NUM"),
                        ]:
                            lastnode.prev.name = lastnode.name
                        prevbuf = lastnode.prev
                        lastnode.prev.childs.remove(lastnode)
                        for child in lastnode.childs:
                            child.prev = prevbuf
                            prevbuf.childs.append(child)
                    elif (lastnode.name, lastnode.prev.name) in [
                        ("INTEGER NUMBER", "REAL NUMBER"),
                    ]:
                        prevbuf = lastnode.prev
                        indx = lastnode.prev.childs.index(lastnode)
                        lastnode.prev.childs.remove(lastnode)
                        for child in lastnode.childs:
                            child.prev = prevbuf
                            prevbuf.childs.insert(indx, child)
                            indx += 1
                    else:
                        lastnode.me.isNonterminal = False
                elif not self.__havenonterminalchilds(lastnode):  # step 6
                    break
                break

    def __fixtree(self, ptr):
        '''Merge all declares, gather id, numbers'''

        def _searchid(ptr: NodeStruct):
            for i in ptr.childs:
                if i.name in ['IDENTIFICATOR', 'STRING', 'INTEGER NUMBER', 'REAL NUMBER', 'BOOL VALUE', 'SIGNED NUM']:
                    tmp = ''
                    for j in i.childs:
                        tmp = tmp + j.name
                        j.prev = None
                    i.value = tmp
                    i.childs = []
                else:
                    _searchid(i)
            return

        def _searchvars(ptr: NodeStruct):
            if len(ptr.childs) == 0:
                return
            for i in ptr.childs:
                _searchvars(i)
                if i.name in ['DECLARE A VARIABLE LIST', 'SUGGESTION_LIST']:
                    indx = ptr.childs.index(i)
                    for j in i.childs:
                        j.prev = ptr
                        ptr.childs.insert(indx, j)
                        indx += 1
                    ptr.childs.remove(i)
            return

        def _searchopers(ptr: NodeStruct):
            if len(ptr.childs) == 0:
                return
            for i in ptr.childs:
                _searchopers(i)
                if i.name == '=':
                    i.value = i.name
                    i.name = 'ASSIGNMENT'
                elif i.name in self.operations + self.unaroperations:
                    i.value = i.name
                    i.name = 'OPERATOR'
                elif i.name in ['DECLARE A VARIABLES']:
                    i.value = i.childs[0].name
                    i.childs[0].prev = None
                    i.childs.pop(0)
            return


        _searchid(ptr)
        _searchvars(ptr)
        self.root.childs[0].name = 'PROGRAMM IDENTIFICATOR'
        _searchopers(ptr)
        return

    def __getlastnonterm(self, ptr) -> NodeStruct:
        '''Select the leftmost tree node marked with a nonterminal symbol'''

        def _search(ptr: NodeStruct):
            for i in ptr.childs:
                if i.isNonterminal:
                    return _search(i)
            return ptr

        return _search(ptr)

    def __copytree(self, stree: SyntacticalTree):
        '''Constructor of copying'''

        def _search(ptr1: Node, ptr2: NodeStruct):
            if ptr1.childs:
                for i in ptr1.childs:
                    n = ''
                    flag = True
                    if isinstance(i.left, Rule):
                        n = i.left.name
                    else:
                        n = i.left
                        flag = False
                    newnode = NodeStruct(flag, n, prev=ptr2)
                    ptr2.childs.append(newnode)
                    _search(i, newnode)

        n = str(stree.root.left)
        res = NodeStruct(True, n)
        _search(stree.root, res)
        return res

    def printast(self):
        '''Output of ast tree'''
        def search(ptr: NodeStruct, level):
            print(str(level) + ':' + '|' + level * '+' + '├-' + str(ptr))
            if ptr.childs:
                for i in ptr.childs:
                    search(i, level + 1)

        level = 0
        search(self.root, level)
        print()