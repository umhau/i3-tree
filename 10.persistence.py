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

indentation_pixels  = 8
background_color    = "#3c3b37"
font_color          = "#dcdccc"
font                = "APL385"
font_size           = "9pt"
window_title        = "i3tree" + str(time.time())  # needs to be unique
show_all_workspaces = True

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
item2con = {}  # item2con[QStandardItem] = container ID
item2idx = {}  # item2idx[QStandardItem] = QModelIndex

# I also want to know which tree items are expanded or contracted. Since 
# expanded is more common, I'll just keep a list of the ones that have been 
# manually contracted.

contracted_treeitems = []
expansion_dictionary = {}
not_expanded = {}

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

# left click action
def tree_item_left_clicked(index):
    item = globalmodel.itemFromIndex(index)
    print('index: ' , index)
    print('item:  ' , item)
    print('text:  ' , item.text())
globaltree.clicked[QtCore.QModelIndex].connect(tree_item_left_clicked)

## -- [ main asynchronous loop ] -------------------------------------------- ##

async def main():

    i3 = await Connection(auto_reconnect=True).connect()
    tree = await i3.get_tree()

    

    async def updatetree(conn, event):

        starttime = time.time()

        expansion_dictionary.clear()

        globaltreemodel = globaltree.model()

        # # build dictionaries
        # proxy = globaltree.model()
        # for row in range(proxy.rowCount()):
        #     index = proxy.index(row, 0)
        #     item  = globalmodel.itemFromIndex(index)
        #     # item2idx[item] = index
        #     print('item:  ' , item)
        #     print('index: ' , index)


            # globaltreemodel.expand(index)
        print('item -> index')
        print(item2idx)


        # def check_if_expanded(qt_model, index=QtCore.QModelIndex()):

        #     if index.isValid():

        #         expanded = globaltree.isExpanded(index)
        #         print('index [' , index , '] : expanded : [', expanded , ']')

        #         if not expanded:

        #             item = globalmodel.itemFromIndex(index)
        #             print('text: ' , item.text())

        #             if index not in contracted_treeitems:
        #                 # contracted_treeitems[index] = expanded
        #                 contracted_treeitems.append(index)

        #                 # globaltree.setExpanded(index, False)

        #     for row in range(qt_model.rowCount(index)):
        #         for col in range(qt_model.columnCount(index)):

        #             childIndex = qt_model.index(row, col, index)
                    
        #             for childRow in range(qt_model.rowCount(childIndex)):

        #                 check_if_expanded(qt_model, childIndex)
        #                 print('recursive: ', childRow)

        def getExpandState(model, index=QtCore.QModelIndex()):

            # print('dictionary size: ' , len(expansion_dictionary))

            # set the index expanded state, if it's not the root index:
            # the root index is not a valid index!
            if index.isValid():

                if index not in expansion_dictionary.keys():

                    item = globaltreemodel.itemFromIndex(index)
                    expansion_dictionary[item.data()] = globaltree.isExpanded(index)
                    # 
                    # print('index: ' , index)
                    # print('type:  ' , type(globaltree.isExpanded(index)))
                    # print('item:  ' , item)
                    # print('text:  ' , item.text())
                    # globaltree.setExpanded(index, True)

                    # if not globaltree.isExpanded(index):
                    #     print('container id: ' , item.data())

            # if the index (or root index) has children, set their states
            for row in range(model.rowCount(index)):
                for col in range(model.columnCount(index)):
                    
                    childIndex = model.index(row, col, index)
                    # if the current index has children, set their expand state
                    # using this function, which is recursive
                    for childRow in range(model.rowCount(childIndex)):
                        getExpandState(model, childIndex)

        # check_if_expanded(globaltreemodel)
        getExpandState(globaltreemodel)

        # # print('review of contents:')
        # # print('dictionary size: ' , len(expansion_dictionary))
        # for treeitemindex in expansion_dictionary.keys():
        #     # print('index: ')
        #     # print(treeitemindex)
        #     globaltree.setExpanded(treeitemindex, True)
        #     # item = globaltreemodel.itemFromIndex(treeitemindex)

        print('expansion dictionary:')
        print(expansion_dictionary)

        # print('contracted tree items: ')
        # print(contracted_treeitems)

        tree = await i3.get_tree()
        
        # define the root container - this could be per-workspace or global
        if show_all_workspaces:
            root_container = tree
        else:
            workspace = tree.find_focused().workspace()
            root_container = workspace
        
        # this clears the structure for a total refresh
        globalmodel.setRowCount(0)

        # clears the secondary list for a total refresh
        con2item = {}

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

            # expand the relevant items

            # add the item to the list of processed nodes
            con2item[container_id] = parent.child(parent.rowCount() - 1)

        # print('expanding all tree items manually...')

        # print('expansion dictionary:')
        # print(expansion_dictionary)

        # expand everything, then contract some things selectively
        # globaltree.expandAll()

        # for treeitemindex in expansion_dictionary.keys():
        #     print(treeitemindex)
            # item = globaltreemodel.itemFromIndex(treeitemindex)

        # # this works fine?
        # for row in range(globaltreemodel.rowCount()):
        #     index = globaltreemodel.index(row, 0)
        #     globaltree.expand(index)

        # for container_id in con2item.keys():
        #     if container_id in expansion_dictionary.keys():
        #         if expansion_dictionary[container_id]:
        #             globaltree.expand(index)

        # globaltreemodel = globaltree.model()

        def expand_some_nodes(model, index=QtCore.QModelIndex()):

            # set the index expanded state, if it's not the root index:
            # the root index is not a valid index!
            if index.isValid():

                item = globaltreemodel.itemFromIndex(index)
                try:
                    if expansion_dictionary[item.data()]:
                        globaltree.setExpanded(index, True)
                except:
                    print('new container?')
                    globaltree.setExpanded(index, True)
                # if index not in expansion_dictionary.keys():

                #     item = globaltreemodel.itemFromIndex(index)
                #     expansion_dictionary[item.data()] = globaltree.isExpanded(index)
                    # 
                    # print('index: ' , index)
                    # print('type:  ' , type(globaltree.isExpanded(index)))
                    # print('item:  ' , item)
                    # print('text:  ' , item.text())
                    # globaltree.setExpanded(index, True)

                    # if not globaltree.isExpanded(index):
                    #     print('container id: ' , item.data())

            # if the index (or root index) has children, set their states
            for row in range(model.rowCount(index)):
                for col in range(model.columnCount(index)):
                    
                    childIndex = model.index(row, col, index)
                    # if the current index has children, set their expand state
                    # using this function, which is recursive
                    for childRow in range(model.rowCount(childIndex)):
                        expand_some_nodes(model, childIndex)

        # check_if_expanded(globaltreemodel)
        expand_some_nodes(globaltreemodel)




        # for treeitems_index in contracted_treeitems:
        #     print(treeitems_index)
        #     if treeitems_index.isValid():
        #         print('valid!')
        #         try:
        #             item = globaltreemodel.itemFromIndex(treeitems_index)
        #             print('contents: ' , item.text())
        #             globaltreemodel.setExpanded(treeitems_index, False)
        #         except:
        #             print('failed to parse')
                
        #     else:
        #         print('not valid!')


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
    for i in range(100):
        i3treewindow.command('move left')
    i3treewindow.command('resize set 200')
    i3treewindow.command('border none')
except:
    pass

with loop:
    sys.exit(loop.run_until_complete(main()))