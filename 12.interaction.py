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

indentation_pixels  = 6
background_color    = "#3c3b37"
font_color          = "#dcdccc"
font                = "APL385"
font_size           = "9pt"
window_title        = "i3tree" + str(time.time())  # needs to be unique
show_all_workspaces = True
refocus_on_i3tree   = False

## -- [ gui components ] ---------------------------------------------------- ##

app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

programwindow = QWidget()
colors_config = \
    "background-color: " + background_color + " ; " \
    + "color: "          + font_color       + " ; " \
    + "font-family: "    + font             + " ; " \
    + "font-size: "      + font_size        + " ;"
programwindow.setStyleSheet(colors_config)

globalmodel = QStandardItemModel()

globaltree = QTreeView(programwindow)
globaltree.header().hide()
globaltree.setModel(globalmodel)
globaltree.setIndentation(indentation_pixels)

globallayout = QVBoxLayout(programwindow)
globallayout.addWidget(globaltree)

## -- [ data structures ] --------------------------------------------------- ##

# I need to track the relationship between three values: the i3 container id, 
# which allows me to manipulate i3 window containers, the entry in my QTreeView
# of the corresponding QStandardItem which displays the container name, and the
# QModelIndex of that QStandardItem which lets me manipulate the QStandardItem.

# There is a function for index2item: item = globalmodel.itemFromIndex(index)

con2item = {}  # con2item[container ID]  = QStandardItem

# I also want to know which tree items are expanded or contracted. Since 
# expanded is more common, I'll just keep a list of the ones that have been 
# manually contracted.

expansion_dictionary = {}  # expansion_dictionary[container ID] = expanded bool

# Note that the QStandardItems have a .data() method, that I can use to track
# which of them are associated with which containers. They currently hold 
# the container ids.

## -- [ interaction control ] ----------------------------------------------- ##

# button to expand all nodes
def expand_all_nodes():
    globaltree.expandAll()
expand_button = QPushButton('expand all')
expand_button.setToolTip('expand the whole tree')
expand_button.move(100,70)
expand_button.clicked.connect(expand_all_nodes)
globallayout.addWidget(expand_button, 1)

# button to expand all nodes
def collapse_all_nodes():
    globaltree.collapseAll()
contract_button = QPushButton('collapse all')
contract_button.setToolTip('collapse the whole tree')
contract_button.move(100,70)
contract_button.clicked.connect(collapse_all_nodes)
globallayout.addWidget(contract_button, 2)

# button to close program
def close_program():
    sys.exit()
exit_button = QPushButton('exit')
exit_button.setToolTip('close i3tree')
exit_button.move(100,70)
exit_button.clicked.connect(close_program)
globallayout.addWidget(exit_button, 3)

# left click action
def tree_item_left_clicked(index):
    item = globalmodel.itemFromIndex(index)
    container_id = int(item.data())

    print('index: ' , index)
    print('item:  ' , item)
    print('text:  ' , item.text())
    print('data:  ' , container_id)

    i3_singlethread = Connection_singlethread()
    tree_singlethread = i3_singlethread.get_tree()

    clicked_window = tree_singlethread.find_by_id(container_id)
    clicked_window.command('focus')

    if refocus_on_i3tree:
        i3treewindow = tree_singlethread.find_named(window_title)[0]
        i3treewindow.command('focus')
        
globaltree.clicked[QtCore.QModelIndex].connect(tree_item_left_clicked)


## -- [ main asynchronous loop ] -------------------------------------------- ##

async def main():

    i3 = await Connection(auto_reconnect=True).connect()

    # [ --- update the gui --- ] --------------------------------------------- #

    async def updatetree(conn, event):


        # [ --- initial preparations --- ] ----------------------------------- #

        starttime = time.time()

        try:
            tree = await i3.get_tree()
        except:
            print('failed to parse json!')
            return

        # define the root container - this could be per-workspace or global
        if show_all_workspaces:
            root_container = tree
        else:
            workspace = tree.find_focused().workspace()
            root_container = workspace

        # save a copy of the tree model before it's reset
        globaltreemodel = globaltree.model()

        # clear variables
        expansion_dictionary.clear()
        con2item = {}

        # [ --- figure out which rows are visually collapsed --- ] ----------- #

        def getExpandState(model, index=QtCore.QModelIndex()):

            if index.isValid():
                if index not in expansion_dictionary.keys():
                    item = globaltreemodel.itemFromIndex(index)
                    expansion_dictionary[item.data()] = globaltree.isExpanded(index)

            for row in range(model.rowCount(index)):
                # for col in range(model.columnCount(index)):
                    
                    childIndex = model.index(row, 0, index)

                    for childRow in range(model.rowCount(childIndex)):
                        getExpandState(model, childIndex)

        getExpandState(globaltreemodel)

        # [ --- create the new version of the gui tree --- ] ----------------- #

        # clear the old version 
        globalmodel.setRowCount(0)

        # unique id of the root node
        root_node_unique_id = str(root_container.id)

        # need a base node to attach to
        root = globalmodel.invisibleRootItem()

        # add new windows
        for i3container in root_container.descendants():

            container_id = str(i3container.id)
            parent_id    = str(i3container.parent.id)

            # find the parent
            if parent_id == root_node_unique_id:
                parent = root
            else:
                parent = con2item[parent_id]

            # add the container ID to the item in the GUI
            rowitem = QStandardItem(i3container.name)
            rowitem.setData(container_id)

            # add the item to the GUI
            parent.appendRow(rowitem)

            # add the item to the list of processed nodes
            con2item[container_id] = parent.child(parent.rowCount() - 1)

        # [ --- expand and collapse the rows to match prior --- ] ------------ #

        def expand_some_nodes(model, index=QtCore.QModelIndex()):

            if index.isValid():

                item = globaltreemodel.itemFromIndex(index)

                try:
                    if expansion_dictionary[item.data()]:
                        globaltree.setExpanded(index, True)
                except:
                    # print('new container?')
                    globaltree.setExpanded(index, True)

            # if the index (or root index) has children, set their states
            for row in range(model.rowCount(index)):
                for col in range(model.columnCount(index)):
                    
                    childIndex = model.index(row, col, index)
                    # if the current index has children, set their expand state
                    # using this function, which is recursive
                    for childRow in range(model.rowCount(childIndex)):
                        expand_some_nodes(model, childIndex)

        expand_some_nodes(globaltreemodel)

        print("--- %s seconds ---" % (time.time() - starttime))

    i3.on(Event.WINDOW, updatetree) # update on any window change
    i3.on(Event.TICK, updatetree)   # update as soon as it's drawn

    await i3.main()

## -- [ start the program ] ------------------------------------------------- ##

programwindow.setGeometry(300, 100, 600, 300)
programwindow.setWindowTitle(window_title)
programwindow.show()

try:
    i3_singlethread = Connection_singlethread()
    tree_singlethread = i3_singlethread.get_tree()
    i3treewindow = tree_singlethread.find_named(window_title)[0]
    i3treewindow.command('focus')
    # i3treewindow.command('floating enable')
    i3treewindow.floating
    for i in range(100):
        i3treewindow.command('move right')
    i3treewindow.command('resize set 200')
    i3treewindow.command('border none')
except:
    pass

with loop:
    sys.exit(loop.run_until_complete(main()))