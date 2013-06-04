import elementary
import evas
import sortedlist as sl
import random

class derp(object):
    def __init__( self ):
        self.mainWindow = elementary.StandardWindow("Testing", "Elementary Sorted Table")
        self.mainWindow.callback_delete_request_add(lambda o: elementary.exit())
        self.nf = elementary.Naviframe(self.mainWindow)
        self.nf.size_hint_weight_set(evas.EVAS_HINT_EXPAND, evas.EVAS_HINT_EXPAND)
        self.nf.size_hint_align_set(evas.EVAS_HINT_FILL, evas.EVAS_HINT_FILL)
        self.nf.show()
        self.mainWindow.resize_object_add(self.nf)

    def launch( self ):
        self.mainWindow.resize(800, 400)
        self.mainWindow.show()
        self.options_spawn()

    def options_spawn( self, bt=False ):
        #Give this an elementary item to push to view
        slist = sl.SortedList(self.mainWindow, [["Column 1", True], ["Column 2", True], ["Column 3", True], ["Column 4", True]])
        
        for i in range(12):
            slist.pack_new([random.randint(i, 237-3*i), random.randint(i, 237-4*i), random.randint(i, 237-5*i), random.randint(i, 237-6*i)])
        slist.show()

        self.nf.item_simple_push(slist)

if __name__ == "__main__":
    GUI = derp()
    GUI.launch()
    elementary.run()    
    elementary.shutdown()
