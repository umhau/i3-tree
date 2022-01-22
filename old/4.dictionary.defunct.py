from i3ipc.aio import Connection
from i3ipc import Event
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from asyncqt import QEventLoop
import sys
import asyncio
from collections import deque
# from PyQt5.QtCore import *

data = [
    {'unique_id': 11, 'parent_id': 0, 'short_name': '', 'height': ' ', 'weight': ' '},
    {'unique_id': 12, 'parent_id': 11, 'short_name': 'Class 1', 'height': ' ', 'weight': ' '},
    {'unique_id': 3, 'parent_id': 12, 'short_name': 'Lucy', 'height': '162', 'weight': '50'},
    {'unique_id': 4, 'parent_id': 12, 'short_name': 'Joe', 'height': '175', 'weight': '65'},
    {'unique_id': 5, 'parent_id': 11, 'short_name': 'Class 2', 'height': ' ', 'weight': ' '},
    {'unique_id': 6, 'parent_id': 4, 'short_name': 'Lily', 'height': '170', 'weight': '55'},
    {'unique_id': 7, 'parent_id': 6, 'short_name': 'Tom', 'height': '180', 'weight': '75'},
    {'unique_id': 8, 'parent_id': 7, 'short_name': 'Class 3', 'height': ' ', 'weight': ' '},
    {'unique_id': 9, 'parent_id': 8, 'short_name': 'Jack', 'height': '178', 'weight': '80'},
    {'unique_id': 10, 'parent_id': 8, 'short_name': 'Tim', 'height': '172', 'weight': '60'}
]

globalmodel = QStandardItemModel()
globalmodel = QStandardItemModel()
globalmodel.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])

app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
programwindow = QWidget()

globaltree = QTreeView(programwindow)
globallayout = QVBoxLayout(programwindow)
globallayout.addWidget(globaltree)

globaltree.header().setDefaultSectionSize(180)
globaltree.setModel(globalmodel)

def _print(conn, event):
    print(event)

async def main():
    i3 = await Connection(auto_reconnect=True).connect()
    tree = await i3.get_tree()

    async def updatetree(conn, event):

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()



    i3.on(Event.WINDOW, _print)
    await i3.main()


def importData(data):

    globalmodel.setRowCount(0)

    # need a base node to attach to?
    root = globalmodel.invisibleRootItem()

    # list of unique ids of nodes already processed (QStandardItem nodes)
    seen = {}

    # convert data to a nicer format: a (weird) list, holding dictionaries
    values = deque(data)

    # while there's still something left in the unprocessed data
    while values:

        # grab the first value off the left side
        value = values.popleft()

        # special case: is the parent the root node?
        if value['unique_id'] == 11:
            parent = root

        # otherwise, has the parent been processed yet, or has the child 
        # been entered first in the data?
        else:

            # get the parent unique id
            parent_id = value['parent_id']

            # if the parent hasn't been processed yet, put the data back in
            # in the pile - on the bottom
            if parent_id not in seen:
                values.append(value)
                continue

            # the parent has already been processed. Get a pointer to it.
            parent = seen[parent_id]

        # get the unique id of the node
        unique_id = value['unique_id']

        # add the new node to the parent we identified
        parent.appendRow([
            QStandardItem(value['short_name']),
            QStandardItem(value['height']),
            QStandardItem(value['weight'])
        ])

        # add the new node to the list of possible nodes
        seen[unique_id] = parent.child(parent.rowCount() - 1)



importData(data)

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle('QTreeview Example')
programwindow.show()

globaltree.expandAll()

with loop:
    sys.exit(loop.run_until_complete(main()))