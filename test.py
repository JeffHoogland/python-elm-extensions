import random

import efl.elementary as elm
elm.init()
from efl.elementary.window import StandardWindow
from efl.elementary.scroller import Scroller
from efl.elementary.label import Label
from efl.elementary.button import Button
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

import sortedlist as sl

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

ROWS = 15
COLUMNS = 5

class derp(object):
    def __init__( self ):
        win = StandardWindow("Testing", "Elementary Sorted Table")
        win.callback_delete_request_add(lambda o: elm.exit())

        scr = Scroller(win)
        scr.size_hint_weight = EXPAND_BOTH
        win.resize_object_add(scr)

        titles = []
        for i in range(COLUMNS):
            if i == 0:
                titles.append(
                    ("", False)
                    )
            else:
                titles.append(
                    ("Column " + str(i), True if i != 2 else False)
                    )

        slist = sl.SortedList(scr, titles=titles, size_hint_weight=EXPAND_BOTH,
            size_hint_align=FILL_BOTH, homogeneous=True)
        scr.content = slist
        scr.show()

        for i in range(ROWS):
            row = []
            for j in range(COLUMNS):
                if j == 0:
                    btn = Button(slist)
                    btn.text = "Delete row"
                    btn.callback_clicked_add(
                        lambda x, y=row: slist.row_unpack(y, delete=True)
                        )
                    btn.show()
                    row.append(btn)
                else:
                    data = random.randint(0, ROWS*COLUMNS)
                    lb = Label(slist)
                    lb.text=str(data)
                    lb.data["sort_data"] = data
                    lb.show()
                    row.append(lb)
            slist.row_pack(row, sort=False)
        slist.sort_by_column(1)
        slist.show()

        win.resize(600, 400)
        win.show()

if __name__ == "__main__":
    GUI = derp()
    elm.run()
    elm.shutdown()
