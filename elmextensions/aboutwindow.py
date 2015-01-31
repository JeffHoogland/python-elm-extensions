from efl.ecore import Exe
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.window import Window, ELM_WIN_DIALOG_BASIC
from efl.elementary.window import ELM_WIN_DIALOG_BASIC
from efl.elementary.background import Background
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.label import Label, ELM_WRAP_WORD
from efl.elementary.icon import Icon
from efl.elementary.separator import Separator
from efl.elementary.frame import Frame
from efl.elementary.entry import Entry, ELM_TEXT_FORMAT_PLAIN_UTF8, \
            ELM_WRAP_NONE, ELM_WRAP_MIXED
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
EXPAND_VERT = 0.0, EVAS_HINT_EXPAND
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
FILL_VERT = 0.5, EVAS_HINT_FILL

def xdg_open(url_or_file):
    Exe('xdg-open "%s"' % url_or_file)

class AboutWindow(Window):
    def __init__(self, parent, title="About", standardicon="dialog-information", \
                        version="N/A", authors="No One", \
                        licen="GPL", webaddress="", info="Something, something, turtles"):
        Window.__init__(self, title, ELM_WIN_DIALOG_BASIC, autodel=True)
        
        background = Background(self, size_hint_weight=EXPAND_BOTH)
        self.resize_object_add(background)
        background.show()

        fr = Frame(self, style='pad_large', size_hint_weight=EXPAND_BOTH,
                   size_hint_align=FILL_BOTH)
        self.resize_object_add(fr)
        fr.show()

        hbox = Box(self, horizontal=True, padding=(12,12))
        fr.content = hbox
        hbox.show()

        vbox = Box(self, align=(0.0,0.0), padding=(6,6),
                   size_hint_weight=EXPAND_VERT, size_hint_align=FILL_VERT)
        hbox.pack_end(vbox)
        vbox.show()

        # icon + version
        ic = Icon(self, standard=standardicon, size_hint_min=(64,64))
        vbox.pack_end(ic)
        ic.show()

        lb = Label(self, text=('Version: %s') % version)
        vbox.pack_end(lb)
        lb.show()

        sep = Separator(self, horizontal=True)
        vbox.pack_end(sep)
        sep.show()

        # buttons
        bt = Button(self, text=(title), size_hint_align=FILL_HORIZ)
        bt.callback_clicked_add(lambda b: self.entry.text_set(info))
        vbox.pack_end(bt)
        bt.show()

        bt = Button(self, text=('Website'),size_hint_align=FILL_HORIZ)
        bt.callback_clicked_add(lambda b: xdg_open(webaddress))
        vbox.pack_end(bt)
        bt.show()

        bt = Button(self, text=('Authors'), size_hint_align=FILL_HORIZ)
        bt.callback_clicked_add(lambda b: self.entry.text_set(authors))
        vbox.pack_end(bt)
        bt.show()

        bt = Button(self, text=('License'), size_hint_align=FILL_HORIZ)
        bt.callback_clicked_add(lambda b: self.entry.text_set(licen))
        vbox.pack_end(bt)
        bt.show()

        # main text
        self.entry = Entry(self, editable=False, scrollable=True, text=info,
                        size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.entry.callback_anchor_clicked_add(lambda e,i: xdg_open(i.name))
        hbox.pack_end(self.entry)
        self.entry.show()

        self.resize(400, 200)
        self.show()
