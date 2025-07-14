import sys
import app
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from pyvis import network

# class NoteItem(QTextDocument):
    
#     def __init__(self, id : str):
        
#         self.note =  app.Note(id)

class NoteNetwork():
    
    def __init__(self, notes : list[app.Note] = app.user_notes.get()):
        self.notes = notes
        self.network = network.Network()
        for note in self.notes:
            self.network.add_node(note.name)
        for note in self.notes:
            for note_reference in note.references:
                self.network.add_edge(note.name, note_reference)
    
    def return_html(self, physics : bool = True):
        self.network.toggle_physics(physics)
        self.network.generate_html()
        return self.network.html
    
class NoteNetworkView(QWebEngineView):
    
    def __init__(self, note_network : NoteNetwork, physics : bool = True, debug : bool = False):
        super().__init__()
        
        self.setZoomFactor(0.65)
        self.note_network = note_network
        
        if debug:
            self.loadStarted.connect(lambda : print("loading started"))
            self.loadProgress.connect(lambda progress : print(f"loading {progress}%"))
            self.loadFinished.connect(lambda : print("loading finished"))
        
        self.render(physics)
    
    def render(self, physics : bool = True):
        self.setHtml(self.note_network.return_html(physics))
    
        
class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.shown = None
        
        self.layout = QVBoxLayout()
        
        self.texteditor = QTextEdit()
        self.note_network = NoteNetwork()
        self.network_view = NoteNetworkView(self.note_network, debug=True, physics=False)
    
        # self.network_view.loadStarted.connect(self.hide)
        # self.network_view.loadFinished.connect(lambda : self.show() if self.shown else self.hide())
        
        self.layout.addWidget(self.network_view)
        self.layout.addWidget(self.texteditor)
        
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
    
    #sets shown to true -- window may still not be shown as loading isnt finished but once done it will know what to set it to
    def show(self, *args):
        self.shown = True
        super().show(*args)
        
    
Application = QApplication(sys.argv)
window = Window()

window.show()

Application.exec()



