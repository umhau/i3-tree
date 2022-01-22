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
globaltree.setIndentation(10)

def _print(conn, event):
    print(event)

async def main():
    i3 = await Connection(auto_reconnect=True).connect()
    tree = await i3.get_tree()

    async def updatetree(conn, event):

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()

        # define the root container - this could be per-workspace or global
        root_container = workspace

        print(workspace.name)
        print(type(workspace))
        print(type(workspace.descendants()))
        print('workspace id: ', workspace.id)

        print('============================================================')

        globalmodel.setRowCount(0)

        # globaltree.clear()

        # need a base node to attach to?
        root = globalmodel.invisibleRootItem()

        # unique id of the root node
        root_node_unique_id = str(root_container.id)

        # list of containers to be processed
        containerlist = root_container.descendants()

        # list of unique ids of nodes already processed (QStandardItem nodes)
        processed_nodes = {}

        # convert data to a nicer format: a (weird) list, holding i3 containers
        # containerlist = containerlist

        for container in containerlist: 

            print('------------------------------------------------------------')

            container_id = str(container.id)
            parent_id = str(container.parent.id)

            print('container id: ', container_id)
            print('parent    id: ', parent_id)

            print('id format: ' , type(container.id))

            # special case: is this the root node?
            if parent_id == root_node_unique_id:
                parent = root
                print('[ this is the root node ]')
                print('parent type: ' , type(parent))

            # otherwise, find the parent of each successive node and attach
            else:
                print('[ not root ]')
                
                # the parent has already been processed. Get a pointer to it.
                parent = processed_nodes[parent_id]

            # get the unique id of the node
            unique_id = container_id

            # add the new node to the parent we identified
            parent.appendRow([
                QStandardItem(container.name),
                QStandardItem(container_id),
                QStandardItem(container.type)
            ])

            # # add the new node to the list of possible nodes
            # processed_nodes[unique_id] = parent.child(parent.rowCount() - 1)
            processed_nodes[unique_id] = parent.child(parent.rowCount() - 1)

        print('nodes list: ' , processed_nodes)

        globaltree.expandAll()

    i3.on(Event.WINDOW, updatetree)
    await i3.main()

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle('QTreeview Example')
programwindow.show()

globaltree.expandAll()

with loop:
    sys.exit(loop.run_until_complete(main()))