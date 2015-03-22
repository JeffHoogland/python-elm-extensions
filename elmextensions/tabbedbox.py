# encoding: utf-8

from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL
from efl.elementary.box import Box
from efl.elementary.button import Button
from efl.elementary.icon import Icon
from efl.elementary.separator import Separator
from efl.elementary.scroller import Scroller
from efl.elementary.naviframe import Naviframe

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5
EXPAND_NONE = 0.0, 0.0
ALIGN_CENTER = 0.5, 0.5
ALIGN_RIGHT = 1.0, 0.5
ALIGN_LEFT = 0.0, 0.5

class TabbedBox(Box):
    def __init__(self, parent_widget, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.tabs = []
        self.currentTab = None
        self.tabChangedCallback = None
        self.closeCallback = None
        self.emptyCallback = None

        self.scr = Scroller(self, size_hint_weight=EXPAND_HORIZ,
                           size_hint_align=FILL_BOTH)
        self.scr.content_min_limit(False, True)

        self.buttonBox = Box(self.scr, size_hint_weight=EXPAND_HORIZ,
                           align=ALIGN_LEFT)
        self.buttonBox.horizontal = True
        self.buttonBox.show()

        self.scr.content = self.buttonBox
        self.scr.show()
        
        self.nf = Naviframe(self, size_hint_weight=EXPAND_BOTH,
                               size_hint_align=FILL_BOTH)
        self.nf.show()

        self.pack_end(self.scr)
        self.pack_end(self.nf)
        
    def addTab(self, widget, tabName, canClose=True, disabled=False):
        self.tabs.append(widget)

        btn = Button(self.buttonBox, style="anchor", size_hint_align=ALIGN_LEFT)
        btn.text = tabName
        btn.data["widget"] = widget
        btn.disabled = disabled
        btn.callback_clicked_add(self.showTab, widget)
        btn.show()

        icn = Icon(self.buttonBox)
        icn.standard_set("gtk-close")
        icn.show()

        cls = Button(self.buttonBox, content=icn, style="anchor", size_hint_align=ALIGN_LEFT)
        cls.data["widget"] = widget
        cls.callback_clicked_add(self.closeTab)
        cls.disabled = disabled
        if canClose:
            cls.show()

        sep = Separator(self.buttonBox, size_hint_align=ALIGN_LEFT)
        sep.show()

        self.buttonBox.pack_end(btn)
        self.buttonBox.pack_end(cls)
        self.buttonBox.pack_end(sep)

        #Arguments go: btn, cls, sep
        widget.data["close"] = cls
        widget.data["button"] = btn
        widget.data["sep"] = sep
        
        self.showTab(widget=widget)
    
    def disableTab(self, tabIndex):
        btn, cls = self.tabs[tabIndex].data["button"], self.tabs[tabIndex].data["close"]
        btn.disabled = True
        cls.disabled = True
        
    def enableTab(self, tabIndex):
        btn, cls = self.tabs[tabIndex].data["button"], self.tabs[tabIndex].data["close"]
        btn.disabled = False
        cls.disabled = False
    
    def showTab(self, btn=None, widget=None):
        if type(btn) is int:
            widget = self.tabs[btn]
        if widget != self.currentTab:
            if self.currentTab:
                self.currentTab.data["button"].style="anchor"
            self.nf.item_simple_push(widget)
            self.currentTab = widget
            self.currentTab.data["button"].style="widget"
            
            if self.tabChangedCallback:
                self.tabChangedCallback(self, widget)
    
    def closeTab(self, btn):
        if not self.closeCallback:
            self.deleteTab(btn.data["widget"])
        else:
            self.closeCallback(self, btn.data["widget"])
    
    def deleteTab(self, widget):
        if type(widget) is int:
            widget = self.tabs[widget]
        
        del self.tabs[self.tabs.index(widget)]
        
        self.buttonBox.unpack(widget.data["close"])
        self.buttonBox.unpack(widget.data["button"])
        self.buttonBox.unpack(widget.data["sep"])
        
        widget.data["close"].delete()
        widget.data["button"].delete()
        widget.data["sep"].delete()
        widget.delete()
        
        if self.currentTab == widget and len(self.tabs):
            self.showTab(widget=self.tabs[0])
            
        if not len(self.tabs) and self.emptyCallback:
            self.emptyCallback(self)
