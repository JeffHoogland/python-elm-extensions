import elementary
import evas

#titles is a list, with each element being a sub list
#[<Display Text>, <Sortable>]

class SortedList(elementary.Scroller):
    def __init__(self, window, titles):
        elementary.Scroller.__init__(self, window)
        self.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)

        self.columns = len(titles)
        self.row_count = 0
        self.sort_row = None
        self.rows = []
        self.header = titles
        self.header_text = []
        for header in titles:
            self.header_text.append(header[0])
        self.win = window

        self.table = tb = elementary.Table(self.win)
        tb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        tb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        tb.show()

        self.content_set(tb)

        self.fresh()

    def pack_new(self, row_add):
        if len(row_add) == self.columns:
            #Good, item has the right number of entries we want
            self.row_count += 1
            self.pack(row_add, self.row_count)
            self.rows.append(row_add)
        else:
            raise Exception("The item you are trying to add to this sorted list has the wrong number of columns!")

    def pack(self, row_add, y_pos):
        count = 0
        for col in row_add:
            lb = elementary.Label(self.win)
            lb.text_set("<div align='center'>%s</div>"%col)
            lb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            lb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            lb.show()
            self.table.pack(lb, count, y_pos, 1, 1)
            count += 1    

    def sort(self, button=False, refresh=False):
        #Put code here to sort based on the column pressed
        #mylist.sort(key=lambda e: e[1]) sorts based on the second element in the sub list
        if not refresh:
            text = button.text
            self.fresh()
            sort_index = self.header_text.index(text)
            if self.sort_row == sort_index:
                self.rows.reverse()
            else:
                self.rows.sort(key=lambda e: e[sort_index])
            self.sort_row = sort_index
        for row in self.rows:
            self.pack(row, self.rows.index(row)+1)

    def refresh(self):
        self.fresh()
        self.sort(refresh=True)
        
    def fresh(self):
        self.table.clear(True)

        count = 0
        for title in self.header:
            if title[1]:
                lb = elementary.Button(self.win)
                lb.text_set(title[0])
                lb.callback_pressed_add(self.sort)
            else:
                lb = elementary.Label(self.win)
                lb.text_set("<div align='center'><b>%s</b></div>"%title[0])
            lb.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
            lb.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
            lb.show()
            self.table.pack(lb, count, 0, 1, 1)
            count += 1
