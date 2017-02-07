import sys
reload(sys) 
sys.setdefaultencoding('utf8')

from efl.elementary.box import Box
from efl.elementary.frame import Frame
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.elementary.list import List
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
ALIGN_CENTER = 0.5, 0.5

def searchList(text, lst):
    for item in lst:
        if text.lower() in item.lower()[:len(text)]:
            return lst.index(item)
    return 0

class SearchableList(Box):
    def __init__(self, parent_widget, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.ourList = ourList = List(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        
        self.keys = []
        
        ourList.go()
        ourList.show()
        
        self.ourItems = []
        
        sframe = Frame(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        sframe.text = "Search"
        self.search = search = Entry(self)
        search.single_line = True
        search.callback_changed_add(self.searchChange)
        sframe.content = search
        search.show()
        sframe.show()
        
        self.pack_end(ourList)
        self.pack_end(sframe)
    
    def callback_item_focused_add( self, ourCB ):
        self.ourList.callback_item_focused_add( ourCB )
    
    def callback_clicked_double_add( self, ourCB ):
        self.ourList.callback_clicked_double_add( ourCB )
    
    def item_append( self, text, ourIcon=None ):
        self.keys.append(text)
        self.keys.sort()
        
        itemSpot = self.keys.index(text)
        
        if not len(self.ourItems) or itemSpot > len(self.ourItems)-1:
            item = self.ourList.item_append(text, icon=ourIcon)
            self.ourItems.append(item)
        else:
            #print("Inserting after item %s"%self.ourItems[itemSpot])
            item = self.ourList.item_insert_before(self.ourItems[itemSpot], text, icon=ourIcon)
            self.ourItems.insert(itemSpot, item)
        
        return item
    
    def items_get( self ):
        return self.ourList.items_get()
    
    def selected_item_get( self ):
        return self.ourList.selected_item_get()
    
    def searchChange( self, entry ):
        #print entry.text
        zeindex = searchList(entry.text, self.keys)
        self.ourItems[zeindex].selected_set(True)
        self.ourItems[zeindex].bring_in()
        self.search.focus = True
