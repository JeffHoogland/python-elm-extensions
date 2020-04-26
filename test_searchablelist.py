import efl.elementary as elm
from efl.elementary.window import StandardWindow
elm.init()
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

from elmextensions import SearchableList

class MainWindow(object):
    def __init__( self ):
        win = StandardWindow("Testing", "Elementary SearchableList")
        win.callback_delete_request_add(lambda o: elm.exit())
        
        ourList = SearchableList(win, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.keys = ["Jeff", "Kristi", "Jacob", "Declan", "Joris", 
                "Timmy", "Tristam"]
        for kbl in self.keys:
            ourList.item_append(kbl)
        ourList.show()
        
        win.resize_object_add(ourList)

        win.resize(600, 400)
        win.show()

if __name__ == "__main__":
    GUI = MainWindow()
    elm.run()
    elm.shutdown()
