import random

import efl.elementary as elm
elm.init()
from efl.elementary.window import StandardWindow
from efl.elementary.label import Label
from efl.elementary.button import Button
from efl.elementary.separator import Separator
from efl.elementary.box import Box
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

from elmextensions import SortedList

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

ROWS = 100
COLUMNS = 7

class derp(object):
    def __init__( self ):
        win = StandardWindow("Testing", "Elementary Sorted Table")
        win.callback_delete_request_add(lambda o: elm.exit())

        titles = []
        for i in range(COLUMNS):
            titles.append(
                    ("Column " + str(i), True if i != 2 else False, 1 if i == 1 else 2)
                    )

        slist = SortedList(win, titles=titles, size_hint_weight=EXPAND_BOTH,
            size_hint_align=FILL_BOTH)

        for i in range(ROWS):
            row = []
            for j in range(COLUMNS):
                if j == 0:
                    btn = Button(slist, size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_BOTH)
                    btn.text = "Delete row"
                    btn.callback_clicked_add(
                        lambda x, y=row: slist.row_unpack(y, delete=True)
                        )
                    btn.show()
                    row.append(btn)
                else:
                    data = random.randint(0, ROWS*COLUMNS)
                    
                                #Add to boxes
                    box = Box(slist, size_hint_weight=EXPAND_BOTH,
                                        size_hint_align=FILL_BOTH)
                    box.horizontal = True
                    sep1 = Separator(slist)
                    sep2 = Separator(slist)
                    box.show()
                    sep1.show()
                    sep2.show()
                    
                    lb = Label(slist, size_hint_weight=EXPAND_BOTH,
                                size_hint_align=FILL_BOTH)
                    lb.text=str(data)
                    box.data["sort_data"] = data
                    lb.show()
                    
                    
                    box.pack_end(sep1)
                    box.pack_end(lb)
                    box.pack_end(sep2)
                    
                    row.append(box)
            slist.row_pack(row, sort=False)
        #slist.sort_by_column(1)
        slist.show()
        
        win.resize_object_add(slist)

        win.resize(600, 400)
        win.show()

if __name__ == "__main__":
    GUI = derp()
    elm.run()
    elm.shutdown()
