from efl import ecore
from efl.elementary.box import Box
from efl.elementary.frame import Frame
from efl.elementary.button import Button
from efl.elementary.entry import Entry
from efl.evas import EVAS_HINT_EXPAND, EVAS_HINT_FILL

EXPAND_BOTH = EVAS_HINT_EXPAND, EVAS_HINT_EXPAND
EXPAND_HORIZ = EVAS_HINT_EXPAND, 0.0
FILL_BOTH = EVAS_HINT_FILL, EVAS_HINT_FILL
FILL_HORIZ = EVAS_HINT_FILL, 0.5

class EmbeddedTerminal(Box):
    def __init__(self, parent_widget, titles=None, *args, **kwargs):
        Box.__init__(self, parent_widget, *args, **kwargs)
        
        self.outPut = Entry(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.outPut.editable_set(False)
        self.outPut.scrollable_set(True)
        self.outPut.show()
        
        frame = Frame(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        frame.text = "Input:"
        frame.autocollapse_set(True)
        frame.collapse_go(True)
        frame.show()
        
        bx = Box(self, size_hint_weight=EXPAND_HORIZ, size_hint_align=FILL_HORIZ)
        bx.horizontal = True
        bx.show()
        
        frame.content = bx
        
        self.inPut = Entry(self, size_hint_weight=EXPAND_BOTH, size_hint_align=FILL_BOTH)
        self.inPut.single_line_set(True)
        self.inPut.callback_activated_add(self.enterPressed)
        self.inPut.show()
        
        enterButton = Button(self)
        enterButton.text = "Execute"
        enterButton.callback_pressed_add(self.enterPressed)
        enterButton.show()
        
        bx.pack_end(self.inPut)
        bx.pack_end(enterButton)
        
        self.pack_end(self.outPut)
        self.pack_end(frame)
        
        self.cmd_exe = None
        self.done_cb = None
    
    def enterPressed(self, btn):
        if not self.cmd_exe:
            self.runCommand(self.inPut.text)
            self.inPut.text = ""
        else:
            ourResult = self.cmd_exe.send("%s\n"%self.inPut.text)
            self.inPut.text = ""
            
    def runCommand(self, command, done_cb=None):
        self.cmd_exe = cmd = ecore.Exe(
            command,
            ecore.ECORE_EXE_PIPE_READ |
            ecore.ECORE_EXE_PIPE_ERROR |
            ecore.ECORE_EXE_PIPE_WRITE
        )
        cmd.on_add_event_add(self.command_started)
        cmd.on_data_event_add(self.received_data)
        cmd.on_error_event_add(self.received_error)
        cmd.on_del_event_add(self.command_done)
        
        self.done_cb = done_cb
    
    def command_started(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("---------------------------------")
        self.outPut.entry_append("<br>")

    def received_data(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("%s"%event.data)
        self.outPut.entry_append("<br>")

    def received_error(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("Error: %s" % event.data)

    def command_done(self, cmd, event, *args, **kwargs):
        self.outPut.entry_append("---------------------------------")
        self.outPut.entry_append("<br>")
        self.cmd_exe = None
        if self.done_cb:
            if callable(self.done_cb):
                self.done_cb()
