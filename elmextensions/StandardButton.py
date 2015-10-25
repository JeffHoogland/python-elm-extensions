from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.button import Button
from efl.elementary.box import Box
from efl.elementary.icon import Icon

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL

def StandardButton(ourParent, ourText, ourIcon=None, ourCB=None, *args, **kwargs):
    icon = Icon(ourParent, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
    icon.standard_set(ourIcon)
    icon.show()
        
    button = Button(ourParent, *args, **kwargs)
    button.text = ourText
    button.content_set(icon)
    button.callback_clicked_add(ourCB)
    
    return button
