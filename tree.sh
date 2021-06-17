#!/bin/bash

i3-msg -t get_tree > tree.json


# Yes, see the ipc docs and specifically the get_tree command (i3-msg -t get_tree).

# You can prototype this using i3ipc-python (or a library in the language of your choice).

# Example:

# import i3ipc

# i3 = i3ipc.Connection()

# for con in i3.get_tree():
#     if con.window and con.parent.type != 'dockarea':
#         print("id = {} class = {} name = {} workspace = {}".format(
#             con.window, con.window_class, con.name, con.workspace().name))

# By the way rofi can do what you are asking: rofi -show window