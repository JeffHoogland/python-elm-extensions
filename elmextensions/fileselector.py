# encoding: utf-8

from efl.elementary.label import Label
from efl.elementary.icon import Icon
from efl.elementary.box import Box
from efl.elementary.list import List
from efl.elementary.genlist import Genlist, GenlistItem, GenlistItemClass, \
    ELM_LIST_COMPRESS
from efl.elementary.button import Button
from efl.elementary.hoversel import Hoversel
from efl.elementary.separator import Separator
from efl.elementary.panes import Panes
from efl.elementary.popup import Popup
from efl.elementary.entry import Entry, ELM_INPUT_HINT_AUTO_COMPLETE
from efl.elementary.image import Image
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL, EVAS_CALLBACK_KEY_DOWN
from efl import ecore

#imported to work around a bug
import efl.elementary.layout

import os
import math
from .easythreading import ThreadedFunction
from collections import deque

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5


class FileGLIC(GenlistItemClass):

    def text_get(self, gl, part, data):
        return data["d"]

    def content_get(self, gl, part, data):
        if part == "elm.swallow.icon":
            return Icon(
                gl,
                standard="gtk-file"
                )

fileglic = FileGLIC(item_style="one_icon")


class DirGLIC(GenlistItemClass):

    def text_get(self, gl, part, data):
        return data["d"]

    def content_get(self, gl, part, data):
        if part == "elm.swallow.icon":
            return Icon(
                gl,
                standard="gtk-directory"
                )

dirglic = DirGLIC(item_style="one_icon")


class FileSelector(Box):
    def __init__(self, parent_widget, defaultPath="", defaultPopulate=True, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)

        self.cancelCallback = None
        self.actionCallback = None
        self.directoryChangeCallback = None
        
        self.threadedFunction = ThreadedFunction()
        self._timer = ecore.Timer(0.02, self.populateFile)

        #Watch key presses for ctrl+l to select entry
        parent_widget.elm_event_callback_add(self.eventsCb)

        self.selectedFolder = None
        self.showHidden = False
        self.currentDirectory = None
        self.focusedEntry = None
        self.folderOnly = False
        self.sortReverse = False
        self.addingHidden = False
        self.pendingFiles = deque()
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

        self.fileSelectorBox = Panes(self, content_left_size=0.3,
                      size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
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
        self.fileSortButton.text = u"⬆ Name"
        self.fileSortButton.callback_pressed_add(self.sortData)
        self.fileSortButton.show()
        
        self.fileList = Genlist(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH, homogeneous=True,
                mode=ELM_LIST_COMPRESS)
        self.fileList.callback_activated_add(self.fileDoubleClicked)
        self.fileList.show()
        
        self.previewImage = previewImage = Image(self)
        #previewImage.size_hint_weight = EXPAND_BOTH
        previewImage.size_hint_align = FILL_BOTH
        previewImage.show()
        
        self.fileListBox.pack_end(self.fileSortButton)
        self.fileListBox.pack_end(self.fileList)
        self.fileListBox.pack_end(self.previewImage)

        self.fileSelectorBox.part_content_set("left", self.bookmarkBox)
        self.fileSelectorBox.part_content_set("right", self.fileListBox)

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
        cancelIcon.standard_set("exit")
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
        
        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                size_hint_align=FILL_BOTH)
        con.standard_set("folder-new")
        con.show()
        
        self.createFolderButton = Button(self, size_hint_weight=(0.0, 0.0),
                size_hint_align=(1.0, 0.5), content=con)
        self.createFolderButton.text = "Create Folder  "
        self.createFolderButton.callback_pressed_add(self.createFolderButtonPressed)
        self.createFolderButton.show()

        self.buttonBox.pack_end(self.createFolderButton)
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
        
        self.createPopup = Popup(self)
        self.createPopup.part_text_set("title,text", "Create Folder:")

        self.createEn = en = Entry(self, size_hint_weight=EXPAND_HORIZ,
                size_hint_align=FILL_HORIZ)
        en.single_line_set(True)
        en.scrollable_set(True)
        en.show()
        
        self.createPopup.content = en

        bt = Button(self, text="Create")
        bt.callback_clicked_add(self.createFolder)
        self.createPopup.part_content_set("button1", bt)

        bt2 = Button(self, text="Cancel")
        bt2.callback_clicked_add(self.closePopup)
        self.createPopup.part_content_set("button2", bt2)

        if defaultPopulate:
            self.populateFiles(startPath)

    def folderOnlySet(self, ourValue):
        self.folderOnly = ourValue
        
        if not self.folderOnly:
            self.filenameBox.show()
        else:
            self.filenameBox.hide()

    def createFolder(self, obj):
        newDir = "%s%s"%(self.currentDirectory, self.createEn.text)
        os.makedirs(newDir)
        self.closePopup()
        self.populateFiles(self.currentDirectory)

    def createFolderButtonPressed(self, obj):
        self.createEn.text = ""
        self.createPopup.show()
        self.createEn.select_all()
    
    def closePopup(self, btn=None):
        self.createPopup.hide()

    def shutdown(self, obj=None):
        self._timer.delete()
        self.threadedFunction.shutdown()

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

    def populateFile(self):
        pen_file = len(self.pendingFiles)
        if pen_file:
            for _ in range(int(math.sqrt(pen_file))):
                ourPath, d, isDir = self.pendingFiles.popleft()
                self.packFileFolder(ourPath, d, isDir)

        #else:
        #    self._timer.freeze()
        
        return True

    def populateFiles(self, ourPath):
        self.autocompleteHover.hover_end()

        self.pendingFiles.clear()

        if ourPath[:-1] != "/":
            ourPath = ourPath + "/"

        if ourPath != self.filepathEntry.text or not self.showHidden:
            self.addingHidden = False

            if self.directoryChangeCallback:
                self.directoryChangeCallback(ourPath)

            del self.currentSubFolders[:]
            del self.currentFiles[:]
            self.fileList.clear()
        else:
            self.addingHidden = True

        self.filepathEntry.text = ourPath.replace("//", "/")
        self.currentDirectory = ourPath.replace("//", "/")
    
        self.threadedFunction.run(self.getFolderContents)
        #self._timer.thaw()
    
    def getFolderContents(self):
        ourPath = self.currentDirectory
        
        try:
            data = os.listdir(unicode(ourPath))
        except:
            data = os.listdir(str(ourPath))
        
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
            if self.addingHidden and d[0] == ".":
                self.pendingFiles.append([ourPath, d, isDir])
            elif (d[0] != "." or self.showHidden) and not self.addingHidden:
                self.pendingFiles.append([ourPath, d, isDir])

    def packFileFolder(self, ourPath, d, isDir):
        if isDir:
            li = GenlistItem(item_data={"type": "dir", "path": ourPath, "d": d}, item_class=dirglic, func=self.listItemSelected)
        else:
            li = GenlistItem(item_data={"type": "file", "path": ourPath, "d": d}, item_class=fileglic, func=self.listItemSelected)
            
        li.append_to(self.fileList)
        #self.fileList.go()
        #print("Adding: %s %s %s"%(ourPath, d, isDir))

    def fileDoubleClicked(self, obj, item=None, eventData=None):
        if item.data["type"] == "dir":
            self.addButton.disabled = True
            self.removeButton.disabled = True
            self.populateFiles(item.data["path"]+item.text)
        else:
            self.actionButtonPressed(self.actionButton)

    def getGTKBookmarks(self):
        try:
            with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),'r') as f:
                ourBks = []
                for x in f:
                    x = x.split(" ")[0]
                    x = x.replace("%20", " ")
                    x = x.strip()
                    ourBks.append(x)
                return ourBks
        except IOError:
            return []

    def bookmarkDoubleClicked(self, obj, item=None, eventData=None):
        item.selected_set(False)
        self.addButton.disabled = True
        self.removeButton.disabled = True
        self.populateFiles(item.data["path"])

    def listItemSelected(self, item, gl, data):
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
        
        #Update image preview if an image is selected
        if ourFile[-3:] in ["jpg", "png", "gif"]:
            self.previewImage.file_set("%s/%s"%(self.filepathEntry.text, ourFile))
            self.previewImage.size_hint_weight = (1.0, 0.4)
        else:
            self.previewImage.size_hint_weight = (0, 0)

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
        toAppend = "file://%s%s"%(self.filepathEntry.text, self.selectedFolder.text.replace(" ", "%20"))

        con = Icon(self, size_hint_weight=EXPAND_BOTH,
                    size_hint_align=FILL_BOTH)
        con.standard_set("gtk-directory")
        con.show()
        it = self.bookmarksList.item_append(self.selectedFolder.text, icon=con)
        it.data["path"] = "%s%s"%(self.filepathEntry.text, self.selectedFolder.text)

        self.bookmarksList.go()

        self.addButton.disabled = True
        self.removeButton.disabled = False

        with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),'a') as f:
                f.write( toAppend + " " + self.selectedFolder.text + "\n" )

    def removeButtonPressed(self, btn):
        toRemove = "file://%s%s"%(self.filepathEntry.text, self.selectedFolder.text)

        bks = self.getGTKBookmarks()
        bks.remove(toRemove)

        with open(os.path.expanduser('~/.config/gtk-3.0/bookmarks'),'w') as f:
            for b in bks:
                bName = b.split("/")[-1]
                b = b.replace(" ", "%20")
                f.write( b + " " + bName + "\n" )

        self.bookmarksList.clear()
        self.populateBookmarks()

        self.addButton.disabled = False
        self.removeButton.disabled = True

    def setMode(self, ourMode):
        self.mode = ourMode.lower()

        self.actionButton.text = "%s  "%ourMode
        self.actionIcon.standard_set("document-%s"%ourMode.lower())
        
        if self.mode != "save":
            self.createFolderButton.hide()
        else:
            self.createFolderButton.show()

    def eventsCb(self, obj, src, event_type, event):
        if event.modifier_is_set("Control") and event_type == EVAS_CALLBACK_KEY_DOWN:
            if event.key.lower() == "l":
                self.filepathEntry.focus_set(True)
                self.filepathEntry.cursor_end_set()

    def toggleHiddenButtonPressed(self, btn):
        self.showHidden = not self.showHidden
        self.populateFiles(self.filepathEntry.text)
        
    def toggleHidden(self):
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
        if self.actionCallback:
            if not self.folderOnly and self.fileEntry.text:
                self.actionCallback(self, "%s%s"%(self.filepathEntry.text, self.fileEntry.text))
            elif self.folderOnly:
                self.actionCallback(self, "%s"%(self.filepathEntry.text))

    def fileEntryChanged(self, en):
        typed = en.text.split("/")[-1]

        newList = []

        self.focusedEntry = en

        if en == self.filepathEntry:
            for x in self.currentSubFolders:
                if typed in x:
                    if len(newList) < 10:
                        newList.append(x)
                    else:
                        break
        else:
            for x in self.currentFiles:
                if typed in x:
                    if len(newList) < 10:
                        newList.append(x)
                    else:
                        break

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
        if os.path.isdir(en.text) and en.text != self.currentDirectory:
            self.populateFiles(en.text)
            self.filepathEntry.cursor_end_set()
        else:
            #en.text = self.currentDirectory
            pass
    
    def selected_get(self):
        return "%s%s"%(self.filepathEntry.text, self.fileEntry.text)
