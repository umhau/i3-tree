from i3ipc.aio import Connection
from i3ipc import Event
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QTreeView
from asyncqt import QEventLoop
import sys
import asyncio



app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

globaltreeview = QTreeView()
globaltreeitems = []

class TreeNode(object):
    def __init__(self, data):
        self._data = data
        if type(data) == tuple:
            self._data = list(data)
        if type(data) is str or not hasattr(data, '__getitem__'):
            self._data = [data]

        self._columncount = len(self._data)
        self._children = []
        self._parent = None
        self._row = 0

    def data(self, column):
        if column >= 0 and column < len(self._data):
            return self._data[column]

    def columnCount(self):
        return self._columncount

    def childCount(self):
        return len(self._children)

    def child(self, row):
        if row >= 0 and row < self.childCount():
            return self._children[row]

    def parent(self):
        return self._parent

    def row(self):
        return self._row

    def addChild(self, child):
        child._parent = self
        child._row = len(self._children)
        self._children.append(child)
        self._columncount = max(child.columnCount(), self._columncount)

class CustomModel(QtCore.QAbstractItemModel):
    def __init__(self, nodes):
        QtCore.QAbstractItemModel.__init__(self)
        self._root = TreeNode(None)
        for node in nodes:
            self._root.addChild(node)

    def rowCount(self, index):
        if index.isValid():
            return index.internalPointer().childCount()
        return self._root.childCount()

    def addChild(self, node, _parent):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()
        parent.addChild(node)

    def index(self, row, column, _parent=None):
        if not _parent or not _parent.isValid():
            parent = self._root
        else:
            parent = _parent.internalPointer()

        if not QtCore.QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QtCore.QModelIndex()

        child = parent.child(row)
        if child:
            return QtCore.QAbstractItemModel.createIndex(self, row, column, child)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if index.isValid():
            p = index.internalPointer().parent()
            if p:
                return QtCore.QAbstractItemModel.createIndex(self, p.row(), 0, p)
        return QtCore.QModelIndex()

    def columnCount(self, index):
        if index.isValid():
            return index.internalPointer().columnCount()
        return self._root.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return node.data(index.column())
        return None

async def main():
    i3 = await Connection(auto_reconnect=True).connect()
    tree = await i3.get_tree()

    async def updatetree(conn, event):

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()
        # print(workspace.name)
        globaltreeitems.clear()

        for d in workspace.descendants():

            print(d.parent.parent.name)
            # print(d.parent.parent.parent.name)
            # print(d.parent.parent.parent.parent.name)

            print(d.id)

            if d.parent.parent == workspace:
                if not d.window:
                    globaltreeitems.append(TreeNode('↪'))

                    for e in d.descendants():
                        if e.parent == d:
                            globaltreeitems[-1].addChild(TreeNode(e.name))

                else:
                    globaltreeitems.append(TreeNode(d.name))

        globaltreeview.setModel(CustomModel(globaltreeitems))
        globaltreeview.expandAll()
        globaltreeview.show()

    i3.on(Event.WINDOW_FLOATING, updatetree)
    i3.on(Event.WINDOW_FOCUS,    updatetree)
    i3.on(Event.WINDOW_CLOSE,    updatetree)
    i3.on(Event.WINDOW_NEW,      updatetree)
    i3.on(Event.WINDOW_MOVE,     updatetree)

    i3.on(Event.WORKSPACE_FOCUS, updatetree)
    i3.on(Event.WORKSPACE_INIT,  updatetree)

    await i3.main()


globaltreeitems.append(TreeNode('a'))
globaltreeitems.append(TreeNode('a'))
globaltreeitems.append(TreeNode('a'))
globaltreeitems.append(TreeNode('a'))
globaltreeitems[0].addChild(TreeNode('b'))

globaltreeview.setModel(CustomModel(globaltreeitems))   
globaltreeview.show()

with loop:
    sys.exit(loop.run_until_complete(main()))