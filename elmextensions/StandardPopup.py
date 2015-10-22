#Borrowed from ePad error popup done by ylee

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl import elementary
from efl.elementary.box import Box
from efl.elementary.icon import Icon
from efl.elementary.button import Button
from efl.elementary.image import Image
from efl.elementary.popup import Popup
from efl.elementary.label import Label, ELM_WRAP_WORD
from efl.elementary.table import Table
from efl.elementary.need import need_ethumb

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

def StandardPopup(ourParent, ourMsg, ourIcon=None):
    ourPopup = Popup(ourParent, size_hint_weight=EXPAND_BOTH)
    ourPopup.callback_block_clicked_add(lambda obj: ourPopup.delete())

    # Add a table to hold dialog image and text to Popup
    tb = Table(ourPopup, size_hint_weight=EXPAND_BOTH)
    ourPopup.part_content_set("default", tb)
    tb.show()

    # Add dialog-error Image to table
    need_ethumb()
    icon = Icon(ourPopup, thumb='True')
    icon.standard_set(ourIcon)
    # Using gksudo or sudo fails to load Image here
    #   unless options specify using preserving their existing environment.
    #   may also fail to load other icons but does not raise an exception
    #   in that situation.
    # Works fine using eSudo as a gksudo alternative,
    #   other alternatives not tested
    try:
        dialogImage = Image(ourPopup,
                            size_hint_weight=EXPAND_HORIZ,
                            size_hint_align=FILL_BOTH,
                            file=icon.file_get())
        tb.pack(dialogImage, 0, 0, 1, 1)
        dialogImage.show()
    except RuntimeError:
        # An error message is displayed for this same error
        #   when aboutWin is initialized so no need to redisplay.
        pass
    # Add dialog text to table
    dialogLabel = Label(ourPopup, line_wrap=ELM_WRAP_WORD,
                        size_hint_weight=EXPAND_HORIZ,
                        size_hint_align=FILL_BOTH)
    dialogLabel.text = ourMsg
    tb.pack(dialogLabel, 1, 0, 1, 1)
    dialogLabel.show()

    # Ok Button
    ok_btt = Button(ourPopup)
    ok_btt.text = "Ok"
    ok_btt.callback_clicked_add(lambda obj: ourPopup.delete())
    ok_btt.show()

    # add button to popup
    ourPopup.part_content_set("button3", ok_btt)
    
    return ourPopup
