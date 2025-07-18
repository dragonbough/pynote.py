import sys
import app
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import *
from pyvis import network

class NoteNetwork():
    
    def __init__(self, notes : list[app.Note] = app.user_notes.get(), font_color : str = "white", bg_color : str = None, screen_max_height : int = 1080):
        self.notes = notes
        self.bg_color = bg_color
        # cdn resources being in line means i dont need to worry about access to the internet
        self.network = network.Network(font_color=font_color, cdn_resources="in_line", bgcolor=self.bg_color, height=screen_max_height)
        
        for note in self.notes:
            self.network.add_node(note.name)
        for note in self.notes:
            for note_reference in note.references:
                self.network.add_edge(note.name, note_reference)
                
                            
    #sets the options for the nodes and edges in the network
    def update_options(self):
        self.network.set_options(
            """"" 
            const options = {
                
            "configure": {
                "enabled": false
            },
            "nodes": {
                "opacity": 1,
                "fixed": {
                "x": false,
                "y": false
                }
            },
            "edges": {
                "arrows": {
                "to": {
                    "enabled": true
                }
                },
                "color": {
                "inherit": true
                },
                "selfReference": {
                "angle": 0.7853981633974483
                },
                "smooth": false
            },
            "interaction": {
                "selectConnectedEdges": false,
                "hoverConnectedEdges": false
            },
            "physics": {
                "barnesHut": {
                "avoidOverlap": 0.8
                },
                "minVelocity": 0.75
            }
            }
            """""
        )
    
    
    def return_html(self, physics : bool = True):
        self.network.toggle_physics(physics)
        self.update_options()
        html = self.network.generate_html()
        #adds styling to html to remove the white border around the network visualisation
        html = html.replace("<head>", f"<head><style>html, body {{ margin: 0; padding: 0; background-color: {self.bg_color}; }} </style>")
        
        return html
    
class NoteNetworkView(QWebEngineView):
    
    def __init__(self, note_network : NoteNetwork, physics : bool = True, debug : bool = False):
        super().__init__()
        
        self.physics = physics
        #hides scroll bars
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.setZoomFactor(1)
        self.note_network = note_network        
        if debug:
            self.loadStarted.connect(lambda : print("loading started"))
            self.loadProgress.connect(lambda progress : print(f"loading {progress}%"))
            self.loadFinished.connect(lambda : print("loading finished"))
        
        self.render()
    
    def render(self):
        self.setHtml(self.note_network.return_html(self.physics))
    
        
class Window(QMainWindow):
    
    def __init__(self, max_screen_height : int = 1080):
        super().__init__()
        
        self.shown = None
        
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        
        self.tab1layout = QVBoxLayout()
        self.tab1layout.setContentsMargins(0, 0, 0, 0)
        self.tab1layout.setSpacing(0)
        self.tab2layout = QVBoxLayout()
        
        self.tab1.setLayout(self.tab1layout)
        self.tab2.setLayout(self.tab2layout)
                
        self.texteditor = QTextEdit()
        self.note_network = NoteNetwork(bg_color=self.palette().window().color().name(), screen_max_height=max_screen_height)
        self.network_view = NoteNetworkView(self.note_network, debug=True, physics=False)
        
        # self.network_view.loadStarted.connect(self.hide)
        # self.network_view.loadFinished.connect(lambda : self.show() if self.shown else self.hide())
        
        self.tab1layout.addWidget(self.network_view)
        self.tab2layout.addWidget(self.texteditor)
        
        self.tabs.addTab(self.tab1, "Note Network")
        self.tabs.addTab(self.tab2, "Note Editor")
        
        self.setCentralWidget(self.tabs)
        
    
    #sets shown to true -- window may still not be shown as loading isnt finished but once done it will know what to set it to
    def show(self, *args):
        self.shown = True
        super().show(*args)
        
    
Application = QApplication(sys.argv)
height = Application.primaryScreen().size().height()
window = Window(height)

window.show()

Application.exec()