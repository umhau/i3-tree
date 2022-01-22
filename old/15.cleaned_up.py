from i3ipc.aio import Connection
from i3ipc import Event
from i3ipc import Connection as Connection_singlethread
from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QPushButton, QVBoxLayout
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor, QLinearGradient
from PyQt5 import QtCore
from asyncqt import QEventLoop
import sys
import asyncio
from collections import deque
from screeninfo import get_monitors
from json import loads
from os import popen
import atexit
import time
from pynput.mouse import Button, Controller
# from pynput import mouse

## TODO

# if the clicked window is on the same workspace / output as the tree, refocus
# the tree after focusing the window. Should fix some of the issues there.

## -- [ variables ] --------------------------------------------------------- ##

window_width_pixels = 250
indentation_pixels  = 6
background_color    = "#3c3b37"
gradient_color      = "#494844"
font_color          = "#dcdccc"
font                = "APL385"

font_size           = "8pt"
row_vertical_size   = 24
gradient_center     = int(row_vertical_size/2)

window_title        = "i3tree" + str(time.time())  # needs to be unique

# no good way yet to reliably detect bar heights, so just hardcode for now. 
# (bar height is generally 10 pixels more than the font size, unless specified 
# separately)
# sidebars aren't possible in i3 (which is why this project is so 
# hacked-together).

bar_height_bottom   = 20
bar_height_top      = 0

# showing all workspaces slows it down considerably: 1.3 vs 0.02 seconds
show_all_workspaces = True

# button to toggle whether or not all workspaces are shown
workspaces_button = False

# button to close the program (otherwise just close like any other window)
exit_button       = False

# button to collapse or expand all the rows
show_exp_coll_btns  = False

# how does the user indicate which monitor screen the program should attach to?
# and how does the user indicate which side of that screen it should attach to?
# use a menu button? Or just use a config file?

# put the program window on the left or right side of the screen
window_on_right     = False

# by default, attach to the primary monitor screen.
# if the user specifies otherwise, try and use that.

user_chosen_output  = 'HDMI-4'

# for now, we're going to attach to the currently focused output.

## -- [ gui components ] ---------------------------------------------------- ##

app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

# set the appearance of the window as a whole
programwindow = QWidget()

colors_config_whole_window = \
    "background-color: " + background_color + " ; " \
    + "color: "          + font_color       + " ; " \
    + "font-family: "    + font             + " ; " \
    + "font-size: "      + font_size        + " ; "

programwindow.setStyleSheet(colors_config_whole_window)

globalmodel = QStandardItemModel()

globaltree = QTreeView(programwindow)
globaltree.header().hide()
globaltree.setModel(globalmodel)
globaltree.setIndentation(indentation_pixels)
globaltree.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

globallayout = QVBoxLayout(programwindow)
globallayout.addWidget(globaltree)

# mouse controller
mouse = Controller()

## -- [ data structures ] --------------------------------------------------- ##

con2item = {}  # con2item[container ID]  = QStandardItem
expansion_dictionary = {}  # expansion_dictionary[container ID] = expanded bool

# Note that the QStandardItems have a .data() method, that I can use to track
# which of them are associated with which containers. They currently hold 
# the container ids.

## -- [ interaction control ] ----------------------------------------------- ##

if show_exp_coll_btns:

    # button to expand all nodes
    def expand_all_nodes():
        globaltree.expandAll()
    expand_button = QPushButton('expand all')
    expand_button.setToolTip('expand the whole tree')
    expand_button.move(100,70)
    expand_button.clicked.connect(expand_all_nodes)
    globallayout.addWidget(expand_button, 1)

    # button to collapse all nodes
    def collapse_all_nodes():
        globaltree.collapseAll()
    contract_button = QPushButton('collapse all')
    contract_button.setToolTip('collapse the whole tree')
    contract_button.move(100,70)
    contract_button.clicked.connect(collapse_all_nodes)
    globallayout.addWidget(contract_button, 2)

if workspaces_button:
    
    # button to show / hide all but the present workspace
    def show_hide_other_workspaces():

        global show_all_workspaces

        if show_all_workspaces:
            show_all_workspaces = False
        else:
            show_all_workspaces = True

    showhide_button = QPushButton('toggle all workspaces')
    showhide_button.setToolTip('collapse the whole tree')
    showhide_button.move(100,70)
    showhide_button.clicked.connect(show_hide_other_workspaces)
    globallayout.addWidget(showhide_button, 3)

if exit_button:

    # button to close program
    def close_program():
        sys.exit()

    exit_button = QPushButton('exit')
    exit_button.setToolTip('close i3tree')
    exit_button.move(100,70)
    exit_button.clicked.connect(close_program)
    globallayout.addWidget(exit_button, 4)

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

    # https://pynput.readthedocs.io/en/latest/mouse.html#monitoring-the-mouse
    # https://stackoverflow.com/questions/53354072/python-pynput-how-to-get-relative-mouse-position-on-change

    mouse_starting_point = mouse.position

    # get pointer position
    print('The current pointer position is {0}'.format(mouse_starting_point))

    # focus the new window
    clicked_window.command('focus')

    # refocus the tree window (moves pointer to center of window)
    i3treewindow = tree_singlethread.find_named(window_title)[0]
    i3treewindow.command('focus')

    # put pointer back where it was
    mouse.position = mouse_starting_point
        
globaltree.clicked[QtCore.QModelIndex].connect(tree_item_left_clicked)


## -- [ functions ] --------------------------------------------------------- ## 


def ipc_query(req="command", msg=""):
    ans = popen("i3-msg -t " + req + " " +  msg).readlines()[0]
    return loads(ans)

def alter_gap_on_current_workspace(new_width):

    if window_on_right:
        chosenside = 'right'
    else:
        chosenside = 'left'

    ipc_query(msg="'gaps " + chosenside + " current set " + str(new_width) + "'")

## -- [ main asynchronous loop ] -------------------------------------------- ##

async def main():

    # set gradient appearance
    gradient = QLinearGradient(0, 0, 0, gradient_center)
    gradient.setSpread(QLinearGradient.ReflectSpread)
    gradient.setColorAt(0.0, QColor(background_color))
    gradient.setColorAt(1.0, QColor(gradient_color))
    brush = QBrush(gradient)

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

            if not 'con' == str(i3container.type):
                print(str(i3container.type))

            # print('is floating? ' , i3container.type)
            if 'floating_con' in str(i3container.type):
                continue

            # don't include the i3tree in the list of program windows
            elif window_title in str(i3container.name):
                continue

            # skip the portion of the tree with the scratchpad window (skipping
            # the top level item will also skip its children)
            elif '__i3' == str(i3container.name):
                continue

            # don't include docks in the list
            elif 'topdock' == str(i3container.name):
                continue
            elif 'bottomdock' == str(i3container.name):
                continue

            container_id = str(i3container.id)
            parent_id    = str(i3container.parent.id)

            # if str(i3container.type) == 'workspace':

            #     print('this should be a top level parent')



            # find the parent(s)
            if parent_id == root_node_unique_id:
                parent = root
            else:
                try:
                    parent = con2item[parent_id]
                except:
                    pass
                    # print("no parent found! skipping.")

            # add the container ID to the item in the GUI
            rowitem = QStandardItem(i3container.name)
            rowitem.setData(container_id)

            # add visual gradient
            rowitem.setBackground(brush)

            # change vertical height of row
            rowitem.setSizeHint(QtCore.QSize(20,row_vertical_size))

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

    async def gaps_follow_treewindow(conn, event):

        print('resetting gaps to 0')
        ipc_query(msg="'gaps right all set 0'")
        ipc_query(msg="'gaps left  all set 0'")

        if window_on_right:
            chosenside = 'right'
        else:
            chosenside = 'left'

        print('updating current gap to chosen width')
        ipc_query(msg="'gaps " + chosenside + " current set " + str(window_width_pixels) + "'")

    i3.on(Event.WINDOW, updatetree) # update on any window change
    i3.on(Event.TICK, updatetree)   # update as soon as it's drawn
    i3.on(Event.WORKSPACE, gaps_follow_treewindow)


    await i3.main()

## -- [ start the program ] ------------------------------------------------- ##


# to place the window, we need to figure some things out.
# - which monitor to put it on
#   * monitor is given as a command argument; otherwise, it should go on the 
#     primary monitor
# - dimensions of that monitor
# - which side of the monitor to put it on

# once we have the info, we have to do several things in order.
# - set it to floating
# - make the window the correct height, width, and put it in the right place
# - set the i3 gap on the correct window, on the correct size
#   * do this last, once the focus is on the correct workspace



# the gap should be changed whenever the workspace is changed, since the only 
# options available are for the current workspace or all of them.

# additionally, the gap should be set twice: reset global gaps to 0, then set the
# current workspace gap.



# get the currently focused display



active_display = None
for w in ipc_query(req="get_workspaces"):
    if w['focused']:
        active_display = w['output']
        print('active display: ' , active_display)

for m in get_monitors():

    if m.name in active_display:

        active_display_height = m.height
        active_display_width  = m.width
        break

print('active display height: ' , active_display_height)
print('active display width:  ' , active_display_width)


# set program dimensions and location -----------------------------------------

# vertical placement: zero is the top of the window (excluding the title bar) 
#                     flush with the top of the monitor. note the title bar, 
#                     and border, is above the top of the monitor

# horizontal placement: zero is the left side of the window flush with the 
#                     left side of the current monitor

width = window_width_pixels

height = active_display_height - bar_height_bottom - bar_height_top

vertical_placement = 0 + bar_height_top

if window_on_right:

    horizontal_placement = active_display_width - window_width_pixels - 2

else:

    horizontal_placement = -2 # active_display_width - window_width_pixels - 2


programwindow.setGeometry(horizontal_placement, vertical_placement, width, height)
programwindow.setWindowTitle(window_title)
programwindow.show()

try:
    i3_singlethread = Connection_singlethread()
    tree_singlethread = i3_singlethread.get_tree()
    i3treewindow = tree_singlethread.find_named(window_title)[0]
    i3treewindow.command('focus')
    i3treewindow.command('floating enable')
    i3treewindow.command('border none')
    i3treewindow.command('sticky toggle')


    # implement the gap
    
    alter_gap_on_current_workspace(window_width_pixels)

    # remember this; could be used to move to another workspace
    # print ipc_query(msg="'workspace " + newworkspace + "; move workspace to output " + active_display + "; workspace " + newworkspace + "'")



    # i3-msg "gaps left current set 0"

    # focused = tree_singlethread.find_focused()

    # outputs = i3_singlethread.get_outputs()

    # for output in outputs:

    #     print(f'output: {output.active}')

        # for con in output:
        #     print(con.name())

    
    # print(f'Focused window: {focused.name}')
    # workspace = focused.workspace()
    # print(f'Focused workspace: {workspace.name}')

    # output = focused.output()
    # print(f'Focused output: {output.name}')


except:
    print('stopped abruptly')
    pass



def exit_handler():
    print('My application is ending!')

    print('resetting gaps to 0')
    ipc_query(msg="'gaps right all set 0'")
    ipc_query(msg="'gaps left  all set 0'")

atexit.register(exit_handler)




with loop:
    sys.exit(loop.run_until_complete(main()))