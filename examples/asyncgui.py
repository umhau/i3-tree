from i3ipc.aio import Connection
from i3ipc import Event
from PyQt5.QtWidgets import QApplication, QWidget
from asyncqt import QEventLoop
import sys
import asyncio

def _print(conn, event):
    print(event)

async def main():
    i3 = await Connection(auto_reconnect=True).connect()
    i3.on(Event.WINDOW, _print)
    await i3.main()

if __name__ == '__main__':

    # establish app
    app = QApplication(sys.argv)

    # async stuff
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    # build the window components
    widget = QWidget()
    widget.show()

    # start it
    with loop:
        sys.exit(loop.run_until_complete(main()))