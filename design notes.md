## design notes

the primary tool should operate independently of anything else - just another window.

secondary tool #1: make the tree window a permanent sidebar.

secondary tool #2: change the automatic layout behavior of the windows. 

alteration #1: the tree window also has taskbar stuff in it - clocks, tools, etc.

recommended alterations - 

- st shows name of the running program in the title
- chrome / firefox always opens in new windows

## display

show [ class | name ]. These two seem to always be present, and can differentiate between e.g. browser and file manager windows.

class also tends to be short, and can help identify windows when the title / name is truncated.

## libraries

- GUI library: https://github.com/Immediate-Mode-UI/Nuklear

If I want to do this in C.