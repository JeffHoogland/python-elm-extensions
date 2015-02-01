# encoding: utf-8

from efl.elementary.label import Label
from efl.elementary.icon import Icon
from efl.elementary.box import Box
from efl.elementary.table import Table
from efl.elementary.frame import Frame
from efl.elementary.list import List, ListItem
from efl.elementary.button import Button
from efl.elementary.hoversel import Hoversel
from efl.elementary.separator import Separator
from efl.elementary.entry import Entry, ELM_INPUT_HINT_AUTO_COMPLETE
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EVAS_CALLBACK_KEY_DOWN

import os

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5

class FileSelector(Box):
    def __init__(self, parent_widget, defaultPath="", defaultPopulate=True, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.cancelCallback = None
        self.actionCallback = None
        self.directoryChangeCallback = None

        #Watch key presses for ctrl+l to select entry
        parent_widget.elm_event_callback_add(self.eventsCb)

        self.selectedFolder = None
        self.showHidden = False
        self.currentDirectory = None
        self.focusedEntry = None
        self.sortReverse = False
        self.currentSubFolders = []
        self.currentFiles = []

        #Mode should be "save" or "load"
        self.mode = "save"

        self.home = os.path.expanduser("~")
        self.root = "/"

        #Label+Entry for File Name
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
        self.fileEntry.callback_changed_user_add(self.fileEntryChanged)
        self.fileEntry.show()

        self.filenameBox.pack_end(fileLabel)
        self.filenameBox.pack_end(self.fileEntry)

        sep = Separator(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        sep.horizontal_set(True)
        sep.show()

        #Label+Entry for File Path
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
        self.filepathEntry.callback_changed_user_add(self.fileEntryChanged)
        self.filepathEntry.callback_unfocused_add(self.filepathEditDone)
        self.filepathEntry.callback_activated_add(self.filepathEditDone)
        #Wish this worked. Doesn't seem to do anything
        #self.filepathEntry.input_hint_set(ELM_INPUT_HINT_AUTO_COMPLETE)

        if defaultPath and os.path.isdir(defaultPath):
            startPath = defaultPath
        else:
            startPath = self.home
        self.filepathEntry.show()

        self.filepathBox.pack_end(fileLabel)
        self.filepathBox.pack_end(self.filepathEntry)

        self.autocompleteHover = Hoversel(self, hover_parent=self)
        self.autocompleteHover.callback_selected_add(self.autocompleteSelected)
        #self.autocompleteHover.show()

        self.fileSelectorBox = Box(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.fileSelectorBox.horizontal = True
        self.fileSelectorBox.show()

        """Bookmarks Box contains:

            - Button - Up Arrow
            - List - Home/Root/GTK bookmarks
            - Box
            -- Button - Add Bookmark
            -- Button - Remove Bookmark"""
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
        self.bookmarksList.callback_activated_add(self.bookmarkDoubleClicked)
        self.bookmarksList.show()

        self.bookmarkModBox = Box(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        self.bookmarkModBox.horizontal = True
        self.bookmarkModBox.show()

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("add")
        con.show()

        self.addButton = Button(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ, content=con)
        self.addButton.callback_pressed_add(self.addButtonPressed)
        self.addButton.disabled = True
        self.addButton.show()

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("remove")
        con.show()

        self.removeButton = Button(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ, content=con)
        self.removeButton.callback_pressed_add(self.removeButtonPressed)
        self.removeButton.disabled = True
        self.removeButton.show()

        self.bookmarkModBox.pack_end(self.addButton)
        self.bookmarkModBox.pack_end(self.removeButton)

        self.bookmarkBox.pack_end(self.upButton)
        self.bookmarkBox.pack_end(self.bookmarksList)
        self.bookmarkBox.pack_end(self.bookmarkModBox)

        #Directory List
        self.fileListBox = Box(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.fileListBox.show()
        
        self.fileSortButton = Button(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        self.fileSortButton.text = u"⬇ Name"
        self.fileSortButton.callback_pressed_add(self.sortData)
        self.fileSortButton.show()
        
        self.fileList = List(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        self.fileList.callback_activated_add(self.fileDoubleClicked)
        self.fileList.show()
        
        self.fileListBox.pack_end(self.fileSortButton)
        self.fileListBox.pack_end(self.fileList)

        self.fileSelectorBox.pack_end(self.bookmarkBox)
        self.fileSelectorBox.pack_end(self.fileListBox)

        #Cancel and Save/Open button
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
        self.actionButton.callback_pressed_add(self.actionButtonPressed)
        self.actionButton.show()

        cancelIcon = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        cancelIcon.standard_set("dialog-cancel")
        cancelIcon.show()

        self.cancelButton = Button(self, size_hint_weight=(0.0, 0.0),
                size_hint_align=(1.0, 0.5), content=cancelIcon)
        self.cancelButton.text = "Cancel  "
        self.cancelButton.callback_pressed_add(self.cancelButtonPressed)
        self.cancelButton.show()

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("gtk-find")
        con.show()

        self.toggleHiddenButton = Button(self, size_hint_weight=(0.0, 0.0),
                size_hint_align=(1.0, 0.5), content=con)
        self.toggleHiddenButton.text = "Toggle Hidden  "
        self.toggleHiddenButton.callback_pressed_add(self.toggleHiddenButtonPressed)
        self.toggleHiddenButton.show()

        self.buttonBox.pack_end(self.toggleHiddenButton)
        self.buttonBox.pack_end(self.cancelButton)
        self.buttonBox.pack_end(self.actionButton)

        self.pack_end(self.filenameBox)
        self.pack_end(sep)
        self.pack_end(self.filepathBox)
        self.pack_end(self.autocompleteHover)
        self.pack_end(self.fileSelectorBox)
        self.pack_end(self.buttonBox)

        self.populateBookmarks()

        if defaultPopulate:
            self.populateFiles(startPath)

    def sortData(self, btn):
        self.sortReverse = not self.sortReverse
        
        if self.sortReverse:
            self.fileSortButton.text = u"⬇ Name"
        else:
            self.fileSortButton.text = u"⬆ Name"
        
        self.populateFiles(self.currentDirectory)

    def populateBookmarks(self):
        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("folder_home")
        con.show()

        it = self.bookmarksList.item_append("Home", icon=con)
        it.data["path"] = self.home

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("drive-harddisk")
        con.show()

        it = self.bookmarksList.item_append("Root", icon=con)
        it.data["path"] = self.root

        it = self.bookmarksList.item_append("")
        it.separator_set(True)

        for bk in self.getGTKBookmarks():
            con = Icon(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
            con.standard_set("gtk-directory")
            con.show()
            it = self.bookmarksList.item_append(bk.split("/")[-1], icon=con)
            it.data["path"] = bk[7:]

    def populateFiles(self, ourPath):
        self.autocompleteHover.hover_end()

        if ourPath[:-1] != "/":
            ourPath = ourPath + "/"

        if ourPath != self.filepathEntry.text or not self.showHidden:
            addingHidden = False

            if self.directoryChangeCallback:
                self.directoryChangeCallback(ourPath)

            self.currentSubFolders = []
            self.currentFiles = []
            self.fileList.clear()
        else:
            addingHidden = True

        data = os.listdir(ourPath)
        self.filepathEntry.text = ourPath.replace("//", "/")
        self.currentDirectory = ourPath.replace("//", "/")

        sortedData = []

        for d in data:
            isDir = os.path.isdir("%s%s"%(ourPath, d))

            if isDir:
                self.currentSubFolders.append(d)
                if self.sortReverse:
                    sortedData.append([1, d])
                else:
                    sortedData.append([0, d])
            else:
                self.currentFiles.append(d)
                if self.sortReverse:
                    sortedData.append([0, d])
                else:
                    sortedData.append([1, d])

        sortedData.sort(reverse=self.sortReverse)
        
        for ourFile in sortedData:
            d = ourFile[1]
            isDir = ourFile[0] if self.sortReverse else not ourFile[0]
            if addingHidden and d[0] == ".":
                self.packFileFolder(ourPath, d, isDir)
            elif (d[0] != "." or self.showHidden) and not addingHidden:
                self.packFileFolder(ourPath, d, isDir)

        self.fileList.go()

    def packFileFolder(self, ourPath, d, isDir):
        con = Icon(self, size_hint_weight=EXPAND_HORIZ,
                    size_hint_align=FILL_HORIZ)
        con.show()

        li = ListItem(d, icon=con, callback=self.listItemSelected)
        
        if isDir:
            con.standard_set("gtk-directory")
            li.data["type"] = "dir"
        else:
            con.standard_set("gtk-file")
            li.data["type"] = "file"
            
        li.data["path"] = ourPath

        li.append_to(self.fileList)

    def fileDoubleClicked(self, obj, item=None, eventData=None):
        if item.data["type"] == "dir":
            self.addButton.disabled = True
            self.removeButton.disabled = True
            self.populateFiles(item.data["path"]+item.text)
        else:
            self.actionButtonPressed(self.actionButton)

    def getGTKBookmarks(self):
        try:
            with open(os.path.expanduser('~/.gtk-bookmarks'),'r') as f:
                return [ x.strip() for x in f ]
        except IOError:
            return []


    def bookmarkDoubleClicked(self, obj, item=None, eventData=None):
        item.selected_set(False)
        self.addButton.disabled = True
        self.removeButton.disabled = True
        self.populateFiles(item.data["path"])

    def listItemSelected(self, lst, item, event_type):
        if item.data["type"] == "dir":
            self.directorySelected(item)
        else:
            self.fileSelected(item.text)
            item.selected_set(False)

    def fileSelected(self, ourFile):
        self.fileEntry.text = ourFile
        self.addButton.disabled = True
        self.removeButton.disabled = True
        self.selectedFolder = None

    def directorySelected(self, btn):
        ourPath = btn.data["path"]
        if btn == self.selectedFolder:
            self.populateFiles(ourPath)
            self.addButton.disabled = True
        else:
            self.selectedFolder = btn

            currentMarks = self.getGTKBookmarks()

            toAppend = "file://%s%s"%(self.filepathEntry.text, self.selectedFolder.text)

            if toAppend not in currentMarks:
                self.addButton.disabled = False
                self.removeButton.disabled = True
            else:
                self.addButton.disabled = True
                self.removeButton.disabled = False

    def upButtonPressed(self, btn):
        ourSplit = self.filepathEntry.text.split("/")
        del ourSplit[-1]
        del ourSplit[-1]
        self.populateFiles("/".join(ourSplit))

    def addButtonPressed(self, btn):
        toAppend = "file://%s%s"%(self.filepathEntry.text, self.selectedFolder.text)

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
        con.standard_set("gtk-directory")
        con.show()
        it = self.bookmarksList.item_append(self.selectedFolder.text, icon=con)
        it.data["path"] = toAppend[7:]

        self.bookmarksList.go()

        self.addButton.disabled = True
        self.removeButton.disabled = False

        with open(os.path.expanduser('~/.gtk-bookmarks'),'a') as f:
                f.write( toAppend + "\n" )

    def removeButtonPressed(self, btn):
        toRemove = "file://%s%s"%(self.filepathEntry.text, self.selectedFolder.text)

        bks = self.getGTKBookmarks()
        bks.remove(toRemove)

        with open(os.path.expanduser('~/.gtk-bookmarks'),'w') as f:
                for b in bks:
                        f.write( b + "\n" )

        self.bookmarksList.clear()
        self.populateBookmarks()

        self.addButton.disabled = False
        self.removeButton.disabled = True

    def setMode(self, ourMode):
        self.mode = ourMode.lower()

        self.actionButton.text = "%s  "%ourMode
        self.actionIcon.standard_set("document-%s"%ourMode.lower())

    def eventsCb(self, obj, src, event_type, event):
        if event.modifier_is_set("Control") and event_type == EVAS_CALLBACK_KEY_DOWN:
            if event.key.lower() == "l":
                self.filepathEntry.focus_set(True)
                self.filepathEntry.cursor_end_set()

    def toggleHiddenButtonPressed(self, btn):
        self.showHidden = not self.showHidden
        self.populateFiles(self.filepathEntry.text)

    def callback_cancel_add(self, cb):
        self.cancelCallback = cb

    def callback_activated_add(self, cb):
        self.actionCallback = cb

    def callback_directory_open_add(self, cb):
        self.directoryChangeCallback = cb

    def cancelButtonPressed(self, btn):
        if self.cancelCallback:
            self.cancelCallback(self)

    def actionButtonPressed(self, btn):
        if self.actionCallback and self.fileEntry.text:
            self.actionCallback(self, "%s%s"%(self.filepathEntry.text, self.fileEntry.text))

    def fileEntryChanged(self, en):
        typed = en.text.split("/")[-1]

        newList = []

        self.focusedEntry = en

        if en == self.filepathEntry:
            for x in self.currentSubFolders:
                if typed in x:
                    newList.append(x)
        else:
            for x in self.currentFiles:
                if typed in x:
                    newList.append(x)

        if self.autocompleteHover.expanded_get():
            self.autocompleteHover.hover_end()

        self.autocompleteHover.clear()

        for x in newList:
            self.autocompleteHover.item_add(x)

        self.autocompleteHover.hover_begin()

    def autocompleteSelected(self, hov, item):
        hov.hover_end()
        if self.focusedEntry == self.filepathEntry:
            self.populateFiles("%s%s"%(self.currentDirectory, item.text))
            self.filepathEntry.cursor_end_set()
        else:
            self.fileEntry.text = item.text
            self.fileEntry.cursor_end_set()

    def filepathEditDone(self, en):
        if os.path.isdir(en.text):
            self.populateFiles(en.text)
            self.filepathEntry.cursor_end_set()
        else:
            #en.text = self.currentDirectory
            pass
    
    def selected_get(self):
        return "%s%s"%(self.filepathEntry.text, self.fileEntry.text)
