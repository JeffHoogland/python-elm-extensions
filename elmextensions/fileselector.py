# encoding: utf-8

from efl.elementary.label import Label
from efl.elementary.icon import Icon
from efl.elementary.box import Box
from efl.elementary.frame import Frame
from efl.elementary.list import List
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

from sortedlist import SortedList

import os

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5

class FileSelector(Box):
    def __init__(self, parent_widget, titles=None, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        parent_widget.elm_event_callback_add(self.eventsCb)

        #Mode should be "save" or "load"
        self.mode = "save"

        self.currentDir = os.path.expanduser("~")
        self.home = os.path.expanduser("~")
        self.root = "/"

        self.filenameBox = Box(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        self.filenameBox.horizontal = True
        self.filenameBox.show()
        
        fileLabel = Label(self, size_hint_weight=(0.15, EVAS_HINT_EXPAND),
                size_hint_align=FILL_HORIZ)
        fileLabel.text = "Filename:"
        fileLabel.show()
        
        self.fileEntry = Entry(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_HORIZ)
        self.fileEntry.single_line_set(True)
        self.fileEntry.scrollable_set(True)
        self.fileEntry.show()
        
        self.filenameBox.pack_end(fileLabel)
        self.filenameBox.pack_end(self.fileEntry)
        
        self.filepathBox = Box(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        self.filepathBox.horizontal = True
        self.filepathBox.show()
        
        fileLabel = Label(self, size_hint_weight=(0.15, EVAS_HINT_EXPAND),
                size_hint_align=FILL_HORIZ)
        fileLabel.text = "Current Folder:"
        fileLabel.show()
        
        self.filepathEntry = Entry(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_HORIZ)
        self.filepathEntry.single_line_set(True)
        self.filepathEntry.scrollable_set(True)
        self.filepathEntry.text = self.home
        self.filepathEntry.show()
        
        self.filepathBox.pack_end(fileLabel)
        self.filepathBox.pack_end(self.filepathEntry)
        
        self.fileSelectorBox = Box(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.fileSelectorBox.horizontal = True
        self.fileSelectorBox.show()
        
        self.bookmarkBox = Box(self, size_hint_weight=(0.3, EVAS_HINT_EXPAND),
                size_hint_align=FILL_BOTH)
        self.bookmarkBox.show()
        
        
        upIcon = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        upIcon.standard_set("go-up")
        upIcon.show()
        
        self.upButton = Button(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ, content=upIcon)
        self.upButton.text = "Up"
        self.upButton.callback_pressed_add(self.upButtonPressed)
        self.upButton.show()
        
        self.bookmarksList = List(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.bookmarksList.show()
        
        self.bookmarkBox.pack_end(self.upButton)
        self.bookmarkBox.pack_end(self.bookmarksList)
        
        #, ("Modified", True, 1)
        headers = (("Name", True, 3), ("Size", True, 1))
        self.fileList = SortedList(self, headers, 0, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.fileList.show()
        
        self.fileSelectorBox.pack_end(self.bookmarkBox)
        self.fileSelectorBox.pack_end(self.fileList)
        
        self.buttonBox = Box(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=(1.0, 0.5))
        self.buttonBox.horizontal = True
        self.buttonBox.show()
        
        self.actionIcon = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.actionIcon.standard_set("document-save")
        self.actionIcon.show()
        
        self.actionButton = Button(self, size_hint_weight=(0.0, 0.0),
                size_hint_align=(1.0, 0.5), content=self.actionIcon)
        self.actionButton.text = "Save  "
        self.actionButton.show()
        
        cancelIcon = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        cancelIcon.standard_set("dialog-cancel")
        cancelIcon.show()
        
        self.cancelButton = Button(self, size_hint_weight=(0.0, 0.0),
                size_hint_align=(1.0, 0.5), content=cancelIcon)
        self.cancelButton.text = "Cancel  "
        self.cancelButton.show()
        
        self.buttonBox.pack_end(self.cancelButton)
        self.buttonBox.pack_end(self.actionButton)
        
        self.pack_end(self.filenameBox)
        self.pack_end(self.filepathBox)
        self.pack_end(self.fileSelectorBox)
        self.pack_end(self.buttonBox)
        
        self.populateBookmarks()
        self.populateFiles(self.home)
        
    def populateBookmarks(self):
        self.bookmarks = self.getGTKBookmarks()
        
        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("folder_home")
        con.show()
        
        it = self.bookmarksList.item_append("Home", icon=con, callback=self.bookmarkClicked)
        it.data["path"] = self.home
        
        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("drive-harddisk")
        con.show()
        
        it = self.bookmarksList.item_append("Root", icon=con, callback=self.bookmarkClicked)
        it.data["path"] = self.root
        
        for bk in self.bookmarks:
            con = Icon(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
            con.standard_set("gtk-directory")
            con.show()
            it = self.bookmarksList.item_append(bk.split("/")[-1], icon=con, callback=self.bookmarkClicked)
            it.data["path"] = bk[7:]
    
    def populateFiles(self, ourPath):
        self.fileList.unpack_all()
        if not ourPath:
            ourPath = "/"
        
        data = os.listdir(ourPath)
        self.filepathEntry.text = ourPath
        
        for d in data:
            if d[0] != ".":
                row = []
                
                box = Box(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
                box.horizontal = True
                box.show()
                
                btn = Button(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
                btn.text = d
                btn.show()
                
                if os.path.isdir("%s/%s"%(ourPath, d)):
                    con = Icon(self, size_hint_weight=(0.25, EVAS_HINT_EXPAND),
                            size_hint_align=FILL_BOTH)
                    con.standard_set("gtk-directory")
                    con.show()
                    box.pack_end(con)
                    btn.callback_pressed_add(self.directorySelected, "%s/%s"%(ourPath, d))
                    box.data["sort_data"] = "1%s"%d
                else:
                    btn.style="anchor"
                    btn.callback_pressed_add(self.fileSelected, ourPath, d)
                    box.data["sort_data"] = "2%s"%d
                
                box.pack_end(btn)
                
                ourSize = os.path.getsize("%s/%s"%(ourPath, d))/1000
                
                siz = Label(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
                siz.text = "%s KB"%ourSize
                siz.data["sort_data"] = ourSize
                siz.show()
                
                '''now = datetime.datetime.now()
                
                ourTime = os.path.getmtime("%s/%s"%(ourPath, d))
                
                tm = Label(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
                tm.text = str("")
                tm.show()'''
                
                row.append(box)
                row.append(siz)
                #row.append(tm)
                
                self.fileList.row_pack(row)
        
        self.fileList.sort_by_column(0)

    def getGTKBookmarks(self):               
        with open(os.path.expanduser('~/.gtk-bookmarks'),'r') as f:
                return [ x.strip() for x in f ]
                
    def bookmarkClicked(self, obj, item=None, ourPath=None):
        self.populateFiles(item.data["path"])
        item.selected_set(False)
    
    def fileSelected(self, btn, ourPath, ourFile):
        self.fileEntry.text = ourFile
        
    def directorySelected(self, btn, ourPath):
        self.populateFiles(ourPath)

    def upButtonPressed(self, btn):
        ourSplit = self.filepathEntry.text.split("/")
        del ourSplit[-1]
        self.populateFiles("/".join(ourSplit))
        
    def setMode(self, ourMode):
        self.mode = ourMode.lower()
        
        self.actionButton.text = "%s  "%ourMode
        self.actionIcon.standard_set("document-%s"%ourMode.lower())
        
    def eventsCb(self, obj, src, event_type, event):
        if event.modifier_is_set("Control"):
            if event.key.lower() == "l":
                self.filepathEntry.focus_set(True)
                self.filepathEntry.cursor_end_set()
