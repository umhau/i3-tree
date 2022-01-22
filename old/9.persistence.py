from i3ipc.aio import Connection
from i3ipc import Event
from i3ipc import Connection as Connection_singlethread
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QPushButton, QVBoxLayout
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
window_title       = "i3tree" + str(time.time())

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

# globaltree.header().setDefaultSectionSize(180)
globaltree.header().hide()
globaltree.setModel(globalmodel)
globaltree.setIndentation(indentation_pixels)

def expand_all_nodes():
    globaltree.expandAll()

button = QPushButton('expand all')
button.setToolTip('expand the whole tree')
button.move(100,70)
button.clicked.connect(expand_all_nodes)
globallayout.addWidget(button, 1)

# expansion_record = {}
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
    tree = await i3.get_tree()

    async def updatetree(conn, event):

        global active_nodes
        global globaltree

        previous_model_state = globaltree.model()

        expansion_record = {}
        expansion_record.clear()

        starttime = time.time()

        # print(globaltree.isExpanded(QtCore.QModelIndex()))
        # index = QtCore.QModelIndex()
        # print(previous_model_state.rowCount(index))
        # print(previous_model_state.columnCount(index))

        def check_if_expanded(qt_model, index=QtCore.QModelIndex()):

            for row in range(qt_model.rowCount(index)):
                for col in range(qt_model.columnCount(index)):

                    childIndex = qt_model.index(row, col, index)
                    expanded_bool = globaltree.isExpanded(childIndex)

                    if not expanded_bool:
                        expansion_record[childIndex] = expanded_bool

                    print('index [' , childIndex , '] : expanded : [', expanded_bool , ']')

                    for childRow in range(qt_model.rowCount(childIndex)):

                        # check_if_expanded(qt_model, childIndex)
                        print('recursive: ', childRow)

        check_if_expanded(previous_model_state)

        print(expansion_record)

        tree = await i3.get_tree()
        workspace = tree.find_focused().workspace()

        # define the root container - this could be per-workspace or global
        root_container = workspace
        # root_container = tree

        # print(workspace.name)
        # print(type(workspace))
        # print(type(workspace.descendants()))
        # print('workspace id: ', workspace.id)

        print('============================================================')

        # list of containers to be processed
        containerlist = root_container.descendants()
        
        # # figure out which containers are expanded
        # for container in containerlist:

        #     container_id = str(container.id)
        #     try:
        #         # print(container.name)
        #         # print(active_nodes[container_id])
        #         # print(globaltree.isExpanded(index))

        #         # print(previous_model_state)
        #         index=QtCore.QModelIndex()
        #         # print(index)
        #         # print(globaltree.isExpanded(index))

        #     except KeyError:
        #         print('no such key')
        #         pass

        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        # this clears the structure for a total refresh
        globalmodel.setRowCount(0)

        # clears the secondary list for a total refresh
        active_nodes = {}

        # unique id of the root node
        root_node_unique_id = str(root_container.id)

        # need a base node to attach to
        root = globalmodel.invisibleRootItem()

        # model index?
        index = 0

        # add new windows
        for container in containerlist:

            # print('------------------------------------------------------------')

            container_id = str(container.id)
            parent_id    = str(container.parent.id)

            # find the parent
            if parent_id == root_node_unique_id:
                parent = root
            else:
                parent = active_nodes[parent_id]

            parent.appendRow(QStandardItem(container.name))

            # # add the node's unique id to the parent's entry
            # parent.append(container_id)
            # print(parent)

            # add the container to the list of processed nodes
            active_nodes[container_id] = parent.child(parent.rowCount() - 1)

        globaltree.expandAll()

        for index, expanded in expansion_record.items():
            globaltree.setExpanded(index, expanded)

        print("--- %s seconds ---" % (time.time() - starttime))

    i3.on(Event.WINDOW, updatetree)

    # just a way to get it to update as soon as it's drawn
    i3.on(Event.TICK, updatetree)

    await i3.main()

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle(window_title)
programwindow.show()



try:
    # format the window
    i3_singlethread = Connection_singlethread()
    tree_singlethread = i3_singlethread.get_tree()
    i3treewindow = tree_singlethread.find_named(window_title)[0]
    i3treewindow.command('focus')
    for i in range(100):
        i3treewindow.command('move left')
    i3treewindow.command('resize set 200')
    i3treewindow.command('border none')
    

except:
    pass



with loop:
    sys.exit(loop.run_until_complete(main()))