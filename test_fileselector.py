import random

import efl.elementary as elm
elm.init()
from efl.elementary.window import StandardWindow
from efl.elementary.label import Label
from efl.elementary.button import Button
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

from elmextensions import FileSelector

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

class MainWindow(object):
    def __init__( self ):
        win = StandardWindow("Testing", "Elementary File Selector")
        win.callback_delete_request_add(lambda o: elm.exit())

        self.fs = fs = FileSelector(win, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        #fs.folderOnlySet(True)
        fs.setMode("Open")
        fs.show()
        
        fs.callback_activated_add(self.showFile)
        fs.callback_cancel_add(lambda o: elm.exit())
        
        win.resize_object_add(fs)

        win.resize(600, 400)
        win.show()
        
    def showFile(self, fs, ourFile):
        print(ourFile)

if __name__ == "__main__":
    GUI = MainWindow()
    elm.run()
    GUI.fs.shutdown()
    elm.shutdown()
