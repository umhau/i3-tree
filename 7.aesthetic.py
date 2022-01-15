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
# globalmodel.setHorizontalHeaderLabels(['Name', 'Height', 'Weight'])

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

# 165 bar {
# 166
# 167   status_command i3status
# 168   font pango:APL385 Unicode 11px
# 169
# 170   colors {
# 171     background #3c3b37
# 172     statusline #dcdccc
# 173
# 174     focused_workspace #93b3a3 #3c3b37 #93b3a3
# 175     active_workspace #ffcfaf #3c3b37 #ffcfaf
# 176     inactive_workspace #636363 #3c3b37 #dcdccc
# 177     urgent_workspace #dca3a3 #3c3b37 #dca3a3
# 178   }

# globaltree.setStyleSheet("background-color: #3c3b37; color: #dcdccc; font-family: APL385; font-size: 10pt;")
# programwindow.setStyleSheet("background-color: #3c3b37")

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
    tree = await i3.get_tree()

    async def updatetree(conn, event):

        starttime = time.time()

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()

        # define the root container - this could be per-workspace or global
        # root_container = workspace
        root_container = tree

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

        for container in containerlist: 

            print('------------------------------------------------------------')

            container_id = str(container.id)
            parent_id    = str(container.parent.id)

            print('container id: ' , container_id)
            print('parent    id: ' , parent_id)

            # # find the parent
            if parent_id == root_node_unique_id:
                parent = root
                print('[     root ]')
            else:
                print('[ not root ]')
                parent = processed_nodes[parent_id]

            # add the node to the parent
            parent.appendRow([
                QStandardItem(container.name),
                QStandardItem(container_id),
                QStandardItem(container.type)
            ])

            # add the container to the list of processed nodes
            processed_nodes[container_id] = parent.child(parent.rowCount() - 1)

        print('nodes list: ' , processed_nodes)

        globaltree.expandAll()

        print("--- %s seconds ---" % (time.time() - starttime))

    i3.on(Event.WINDOW, updatetree)
    await i3.main()

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle(window_title)
programwindow.show()

globaltree.expandAll()

with loop:
    sys.exit(loop.run_until_complete(main()))