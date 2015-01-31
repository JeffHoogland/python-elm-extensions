# encoding: utf-8

from efl.elementary.label import Label
from efl.elementary.box import Box
from efl.elementary.frame import Frame
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5

class FileSelector(Box):
    def __init__(self, parent_widget, titles=None, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

