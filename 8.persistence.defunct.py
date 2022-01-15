from i3ipc.aio import Connection
from i3ipc import Event
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5 import QtCore
from asyncqt import QEventLoop
import sys
import asyncio
from collections import deque

import time

## -- [ variables ] --------------------------------------------------------- ##

indentation_pixels = 10
background_color   = "#3c3b37"
font_color         = "#dcdccc"
font               = "APL385"
font_size          = "10pt"
window_title       = "i3tree"

## -- [ program ] ----------------------------------------------------------- ##

globalmodel = QStandardItemModel()
globalmodel = QStandardItemModel()

app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)
programwindow = QWidget()

globaltree = QTreeView(programwindow)
globallayout = QVBoxLayout(programwindow)
globallayout.addWidget(globaltree)

globaltree.header().setDefaultSectionSize(180)
globaltree.setModel(globalmodel)
globaltree.setIndentation(indentation_pixels)

# dictionary of unique ids of nodes already processed
# {
#   unique_id :: [ QStandardItem_node , [ child_node_id, child_node_id] ]
# }
active_nodes = {}

colors_config = \
    "background-color: " + background_color + " ; " \
    + "color: "          + font_color       + " ; " \
    + "font-family: "    + font             + " ; " \
    + "font-size: "      + font_size        + " ;"

programwindow.setStyleSheet(colors_config)

def _print(conn, event):
    print(event)

async def main():

    i3 = await Connection(auto_reconnect=True).connect()
    # tree = await i3.get_tree()

    async def updatetree(conn, event):

        starttime = time.time()

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()

        # define the root container - this could be per-workspace or global
        root_container = workspace
        # root_container = tree

        print(workspace.name)
        print(type(workspace))
        print(type(workspace.descendants()))
        print('workspace id: ', workspace.id)

        print('============================================================')

        # this clears the structure for a total refresh
        # globalmodel.setRowCount(0)

        # unique id of the root node
        root_node_unique_id = str(root_container.id)

        # need a base node to attach to
        root = [globalmodel.invisibleRootItem(), []]

        # list of containers to be processed
        containerlist = root_container.descendants()

        # add new windows
        for container in containerlist: 

            print('------------------------------------------------------------')

            container_id = str(container.id)
            parent_id    = str(container.parent.id)

            print('container id:   ' , container_id)
            print('parent    id:   ' , parent_id)
            print('container name: ', container.name)

            # find the parent
            if parent_id == root_node_unique_id:
                parent = root
                print('[     root ]')
            else:
                print('[ not root ]')
                parent = active_nodes[parent_id]

            # does the parent already have this node as a known child?
            print(parent[1])
            print(container_id)
            if container_id in parent[1]:

                print('window is not new, ignore it')

            else:

                # add the node to the parent
                parent[0].appendRow([
                    QStandardItem(container.name),
                    QStandardItem(container_id),
                    QStandardItem(container.type)
                ])

                # add the node's unique id to the parent's entry
                parent[1].append(container_id)
                print(parent)

                # add the container to the list of processed nodes
                active_nodes[container_id] = [parent[0].child(parent[0].rowCount() - 1), []]

        # print('nodes list:   ' , active_nodes)

        # globaltree.expandAll()

        print("--- %s seconds ---" % (time.time() - starttime))

    i3.on(Event.WINDOW, updatetree)
    await i3.main()

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle(window_title)
programwindow.show()

globaltree.expandAll()

with loop:
    sys.exit(loop.run_until_complete(main()))