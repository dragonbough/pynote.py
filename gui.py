import sys
import app
from PyQt6.QtCore import (QJsonValue, pyqtSlot)
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextEdit, QApplication)
# from PyQt6.QtGui import *

from PyQt6.QtWebEngineWidgets import (QWebEngineView)
from PyQt6.QtWebEngineCore import (QWebEngineSettings)
from PyQt6.QtWebChannel import *

from pyvis.network import (Network)

class NoteNetwork():

    def __init__(self, notes : app.UserNotes = app.user_notes, font_color : str = "white", bg_color : str = None, screen_max_height : int = 1080):

        self.notes = notes
        self.bg_color = bg_color
        # cdn resources being in line means i dont need to worry about access to the internet
        self.network = Network(font_color=font_color, cdn_resources="in_line", bgcolor=self.bg_color, height=screen_max_height)

        notes = self.notes.get()

        for note in notes:
            self.network.add_node(note.name)
        for note in notes:
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
                "minVelocity": 0.5
            }
            }
            """""
        )


    def return_html(self):
        self.update_options()
        html = self.network.generate_html()
        #adds styling to html to remove the white border around the network visualisation
        #also connects to the qwebchannel system used by QT -- allows for channels that can connect to event listeners in JS
        html = html.replace("<head>", f"""
                            <head>
                            <style>
                            html, body {{ margin: 0; padding: 0; background-color: {self.bg_color}; }}
                            </style>
                            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
                            """)

        #inline js allowing for selection functionality -- on the selectNode event, the "pynote_handler" obj defined later activates its selectNode() pyqt slot
        select_event_script = """

        <script>

        var pynote_handler;

        new QWebChannel(qt.webChannelTransport, function(channel) {
            pynote_handler = channel.objects.pynote_handler;
        });

        network.on("selectNode", function(eventobj) {
            pynote_handler.selectNote(eventobj)
            });

        </script>
        </html>

        """

        html = html.replace("</html>", select_event_script)
        return html

    #this will give you one note or all the notes
    def get_note(self, note_name : str | list[str] = None):

        return self.notes.get(note_name)


class NoteNetworkView(QWebEngineView):

    def __init__(self, note_network : NoteNetwork, debug : bool = False):
        super().__init__()

        self.selected_note = None

        #hides scroll bars
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.note_network = note_network
        if debug:
            self.loadStarted.connect(lambda : print("loading started"))
            self.loadProgress.connect(lambda progress : print(f"loading {progress}%"))
            self.loadFinished.connect(lambda : print("loading finished"))

        #creates a channel linked to the JS injected into the HTML
        self.channel = QWebChannel()
        self.channel.registerObject("pynote_handler", self)
        self.page().setWebChannel(self.channel)


        self.render()

    #Slot connecting to selectNode event in visjs -- sets the selected note, from JSON value returned through QWebChannel
    @pyqtSlot(QJsonValue)
    def selectNote(self, eventobj : QJsonValue):
        self.selected_note = self.note_network.get_note(eventobj.toObject()["nodes"].toArray()[0].toString())
        # app.user_notes.get(note_name)

    def render(self):
        self.setHtml(self.note_network.return_html())


class Window(QMainWindow):

    def __init__(self, max_screen_height : int = 1080):
        super().__init__()


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
        self.graph = NoteNetworkView(self.note_network, debug=True)

        self.tab1layout.addWidget(self.graph)
        self.tab2layout.addWidget(self.texteditor)

        self.tabs.addTab(self.tab1, "Note Graph")
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