from i3ipc.aio import Connection
from i3ipc import Event
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QTreeView
from asyncqt import QEventLoop
import sys
import asyncio

app = QApplication(sys.argv)
loop = QEventLoop(app)
asyncio.set_event_loop(loop)

globalwidget = QWidget()
globallayout = QHBoxLayout()

def _print(conn, event):
    print(event)

    globallayout.addWidget(QPushButton("new-Most"), 3)
    globalwidget.setLayout(globallayout)
    globalwidget.show()

async def main():
    i3 = await Connection(auto_reconnect=True).connect()
    tree = await i3.get_tree()

    workspace = tree.find_focused().workspace()

    for d in workspace.descendants():
        if d.parent.parent.parent == workspace:
            if not d.window:
                print('container:')
                for e in d.descendants():
                    if e.parent == d:
                        print('    [', e.name, ']')
            else:
                print('[', d.name, ']')

    # be more specific about events
    # https://github.com/altdesktop/i3ipc-python/blob/master/i3ipc/events.py
    i3.on(Event.WINDOW_FLOATING, _print)
    i3.on(Event.WINDOW_FOCUS, _print)

    await i3.main()

if __name__ == '__main__':


    globallayout.addWidget(QPushButton("Left-Most"))
    globallayout.addWidget(QPushButton("Center"), 1)
    globallayout.addWidget(QPushButton("Right-Most"), 2)
    
    
    globalwidget.setLayout(globallayout)
    globalwidget.show()

    with loop:
        sys.exit(loop.run_until_complete(main()))