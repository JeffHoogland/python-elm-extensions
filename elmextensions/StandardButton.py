from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

class StandardButton(Button):
    def __init__(self, ourParent, ourText, ourIcon=None, ourCB=None, *args, **kwargs):
        Button.__init__(self, ourParent, *args, **kwargs)
        icon = Icon(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        icon.standard_set(ourIcon)
        icon.show()
        
        self.text = ourText
        self.content_set(icon)
        self.callback_clicked_add(ourCB)
