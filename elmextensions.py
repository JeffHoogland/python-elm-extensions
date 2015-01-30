# encoding: utf-8

from efl import ecore
from efl.elementary.label import Label
from efl.elementary.box import Box
from efl.elementary.table import Table
from efl.elementary.frame import Frame
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.elementary.separator import Separator
from efl.elementary.scroller import Scroller, Scrollable, ELM_SCROLLER_POLICY_OFF, ELM_SCROLLER_POLICY_ON, ELM_SCROLLER_POLICY_AUTO
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

class FileSelector(Box):
    def __init__(self, parent_widget, titles=None, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

class EmbeddedTerminal(Box):
    def __init__(self, parent_widget, titles=None, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)
        
        self.outPut = Entry(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.outPut.editable_set(False)
        self.outPut.scrollable_set(True)
        self.outPut.show()
        
        frame = Frame(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        frame.text = "Input:"
        frame.autocollapse_set(True)
        frame.collapse_go(True)
        frame.show()
        
        bx = Box(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        bx.horizontal = True
        bx.show()
        
        frame.content = bx
        
        self.inPut = Entry(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.inPut.single_line_set(True)
        self.inPut.callback_activated_add(self.enterPressed)
        self.inPut.show()
        
        enterButton = Button(self)
        enterButton.text = "Execute"
        enterButton.callback_pressed_add(self.enterPressed)
        enterButton.show()
        
        bx.pack_end(self.inPut)
        bx.pack_end(enterButton)
        
        self.pack_end(self.outPut)
        self.pack_end(frame)
        
        self.cmd_exe = None
        self.done_cb = None
    
    def enterPressed(self, btn):
        if not self.cmd_exe:
            self.runCommand(self.inPut.text)
            self.inPut.text = ""
        else:
            ourResult = self.cmd_exe.send("%s\n"%self.inPut.text)
            self.inPut.text = ""
            
    def runCommand(self, command, done_cb=None):
        self.cmd_exe = cmd = ecore.Exe(
            command,
            ecore.ECORE_EXE_PIPE_READ |
            ecore.ECORE_EXE_PIPE_ERROR |
            ecore.ECORE_EXE_PIPE_WRITE
        )
        cmd.on_add_event_add(self.command_started)
        cmd.on_data_event_add(self.received_data)
        cmd.on_error_event_add(self.received_error)
        cmd.on_del_event_add(self.command_done)
        
        self.done_cb = done_cb
    
    def command_started(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("---------------------------------")
        self.outPut.entry_append("<br>")

    def received_data(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("%s"%event.data)
        self.outPut.entry_append("<br>")

    def received_error(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("Error: %s" % event.data)

    def command_done(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("---------------------------------")
        self.outPut.entry_append("<br>")
        self.cmd_exe = None
        if self.done_cb:
            if callable(self.done_cb):
                self.done_cb()

class SortedList(Scroller):

    """

    A "spread sheet like" widget for elementary.

    Argument "titles" is a list, with each element being a tuple:
    (<Display Text>, <Sortable>)

    """

    def __init__(self, parent_widget, titles=None, initial_sort=0,
        ascending=True, *args, **kwargs):
        Scroller.__init__(self, parent_widget, *args, **kwargs)
        self.policy_set(ELM_SCROLLER_POLICY_AUTO, ELM_SCROLLER_POLICY_OFF)

        self.mainBox = Box(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.mainBox.show()

        self.header = titles
        self.sort_column = initial_sort
        self.sort_column_ascending = ascending

        self.rows = []
        self.header_row = []
        
        self.headerTbl = Table(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        self.headerTbl.homogeneous_set(True)
        self.headerTbl.show()
        
        self.listTbl = Table(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.listTbl.homogeneous_set(True)
        self.listTbl.show()
        
        self.mainScr = Scroller(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.mainScr.policy_set(ELM_SCROLLER_POLICY_OFF, ELM_SCROLLER_POLICY_AUTO)
        self.mainScr.content = self.listTbl
        self.mainScr.show()
        
        self.lists = []

        #self.pack_end(self.header_box)

        if titles is not None:
            self.header_row_pack(titles)
            
        self.mainBox.pack_end(self.headerTbl)
        self.mainBox.pack_end(self.mainScr)
        
        self.content = self.mainBox
        self.show()

    def header_row_pack(self, titles):

        """Takes a list (or a tuple) of tuples (string, bool, int) and packs them to
        the first row of the table."""

        assert isinstance(titles, (list, tuple))
        for t in titles:
            assert isinstance(t, tuple)
            assert len(t) == 3
            title, sortable, wdth = t
            assert isinstance(title, basestring)
            assert isinstance(sortable, bool)
            assert isinstance(wdth, int)

        def sort_btn_cb(button, col):
            if self.sort_column == col:
                self.reverse()
            else:
                self.sort_by_column(col)

        currentwdth = 0
        for count, t in enumerate(titles):
            title, sortable, wdth = t
            btn = Button(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ, text=title)
            btn.callback_clicked_add(sort_btn_cb, count)
            if not sortable:
                btn.disabled = True
            btn.show()
            self.headerTbl.pack(btn, currentwdth, 0, wdth, 1)
            self.header_row.append(btn)
            
            bx = Box(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
            bx.show()
            
            self.listTbl.pack(bx, currentwdth, 0, wdth, 1)
            self.lists.append(bx)
            
            currentwdth += wdth


    def row_pack(self, row, sort=True):

        """Takes a list of items and packs them to the table."""

        assert len(row) == len(self.header_row), (
            "The row you are trying to add to this sorted list has the wrong "
            "number of items! expected: %i got: %i" % (
                len(self.header_row), len(row)
                )
            )

        self.rows.append(row)
        self.add_row(row)

        if sort:
            self.sort_by_column(self.sort_column)
    
    def add_row(self, row):
        #print "Test %s"%row
        for count, item in enumerate(row):
            self.lists[count].pack_end(item)

    def row_unpack(self, row, delete=False):

        """Unpacks and hides, and optionally deletes, a row of items.

        The argument row can either be the row itself or its index number.

        """
        if isinstance(row, int):
            row_index = row
        else:
            row_index = self.rows.index(row)+1

        # print("row index: " + str(row_index-1))
        # print("length: " + str(len(self.rows)))
        # print("sort_data: " + str(row[self.sort_column].data["sort_data"]))

        row = self.rows.pop(row_index-1)

        for count, item in enumerate(row):
            self.lists[count].unpack(item)
            if delete:
                item.delete()
            else:
                item.hide()

        self.sort_by_column(self.sort_column,
            ascending=self.sort_column_ascending)

    def reverse(self):
        rev_order = reversed(range(len(self.rows)))
        for bx in self.lists:
            bx.unpack_all()
        
        for new_y in rev_order:
            self.add_row(self.rows[new_y])

        lb = self.header_row[self.sort_column].part_content_get("icon")
        if lb is not None:
            if self.sort_column_ascending:
                lb.text = u"⬆"
                self.sort_column_ascending = False
            else:
                lb.text = u"⬇"
                self.sort_column_ascending = True
                
        self.rows.reverse()

    def sort_by_column(self, col, ascending=True):

        assert col >= 0
        assert col < len(self.header_row)

        self.header_row[self.sort_column].icon = None

        btn = self.header_row[col]
        ic = Label(btn)
        btn.part_content_set("icon", ic)
        ic.show()

        if ascending == True: #ascending:
            ic.text = u"⬇"
            self.sort_column_ascending = True
        else:
             ic.text = u"⬆"
             self.sort_column_ascending = False

        orig_col = [
            (i, x[col].data.get("sort_data", x[col].text)) \
            for i, x in enumerate(self.rows)
            ]
        sorted_col = sorted(orig_col, key=lambda e: e[1])
        new_order = [x[0] for x in sorted_col]

        # print(new_order)

        if not ascending:
             new_order.reverse()

        # print(new_order)

        for bx in self.lists:
            bx.unpack_all()

        for new_y in new_order:
            self.add_row(self.rows[new_y])

        self.rows.sort(
            key=lambda e: e[col].data.get("sort_data", e[col].text),
            #reverse=False if ascending else True
            )
        self.sort_column = col

    def update(self):
        self.sort_by_column(self.sort_column, self.sort_column_ascending)
