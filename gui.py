import sys
import app
from PyQt6.QtCore import (QJsonValue, pyqtSlot, pyqtSignal, Qt, QUrl)
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout, QTextBrowser, QApplication)
from PyQt6.QtGui import (QTextDocument, QShortcut, QShortcutEvent, QKeySequence)

from PyQt6.QtWebEngineWidgets import (QWebEngineView)
from PyQt6.QtWebEngineCore import (QWebEngineSettings)
from PyQt6.QtWebChannel import *

from pyvis.network import (Network)

import re


class NoteDocument(QTextDocument):

    def __init__(self, note : app.Note = None):

        super().__init__()

        self.note = note
        self.setMarkdown(self.note.text)

    def get_text(self, text_format : str = "markdown"):

        if text_format == "plain":
            return self.toPlainText()
        elif text_format == "html":
            return self.toHtml()
        elif text_format == "markdown":
            return self.toMarkdown()
        else:
            raise Exception(f"Invalid text format: {text_format}")

    #updates the underlying Note objects text
    def update_text(self):

        self.note.update_text(self.get_text())


class NoteEditor(QTextBrowser):

    new_note_set_signal = pyqtSignal(app.Note)

    def __init__(self, notes : app.UserNotes = app.user_notes):

        super().__init__()

        self.setReadOnly(False)
        self.setTextInteractionFlags(self.textInteractionFlags() | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.setOpenExternalLinks(True)

        self.note_documents = [NoteDocument(note) for note in notes.get()]
        self.textChanged.connect(self.check_for_commands)
        self.textChanged.connect(self.update_note_text)
        self.anchorClicked.connect(self.check_link)

        self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.save_document)


    def save_document(self):

        app.user_notes.update_notes(self.document().note)

    #convenience function for updating the current note's text
    def update_note_text(self):

        self.document().update_text()

    #checks note text for specific markdown commands using regex and replaces with formatted html in real time
    # --- BUG --- INCONSISTENT FORMATTING BETWEEN LINES
    def check_for_commands(self):

        cursor = self.textCursor()

        #DEBUGGING STUFF
        # print("\n------ NEW HTML ------")
        # print(f"\n{self.document().toHtml()}")
        # print("\n------ END HTML ------")

        text = self.document().toPlainText()

        #check note text for markdown LINK using regex -- if so, replace with html link that is clickable
        for match in re.finditer("\\[.+\\] ?\\(.+\\)", text):

            link_match = re.search("\\(.+\\)", match.group())
            caption_match = re.search("\\[.+\\]", match.group())

            link = link_match.group().strip("()")
            caption = caption_match.group().strip("[]").strip()

            # if the cursor is currently in the link section (even if completed), ignore -- user may still be editing
            if link_match.start() < cursor.position() < link_match.end():
                continue

            #if the caption is already a hyperlink dont bother
            cursor.setPosition(caption_match.end())
            if cursor.charFormat().isAnchor():
                continue

            protocol_url_pattern = "^https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            url_pattern = "^[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)$"
            #if the link entered isnt the name of another note -- treat it as any other normal link
            if self.check_in_documents(link) == False:
                #if the link is invalid url as well dont even worry bout reformatting it
                if not(re.match(protocol_url_pattern, link)) and not(re.match(url_pattern, link)):
                    continue

            #sets cursor position to end of the markdown command and then deletes it and replaces with html link

            cursor.setPosition(match.end())

            for i in range(match.end() - match.start()):
                cursor.deletePreviousChar()

            self.insertHtml(f"""<a href="{link}"> {caption} </a>""")

        #replaces hashtags that start a new line with bold headings using regex i made, inserts the right heading level and the heading as html accordingly
        for match in re.finditer("^#{1,6}( +\\S.*|[^ #].*)", text, flags= re.MULTILINE):

            cursor.setPosition(match.end() - 1)

            if cursor.blockFormat().headingLevel() != 0:
                continue

            h_lvl = re.search("^(#{1,6})", match.group()).group().count("#") #returns number of hashtags at start of string
            heading = match.group()[h_lvl : ].strip()

            print(f"created heading: {heading}, h{h_lvl}")

            cursor.setPosition(match.end())

            for i in range(match.end() - match.start()):
                cursor.deletePreviousChar()

            self.insertHtml(f"""<h{h_lvl}>{heading}</h{h_lvl}>""")

    #changes the current note in the editor to the inputted note name
    def set_note(self, note_name : str):
        if self.check_in_documents(note_name):
            self.setDocument([document for document in self.note_documents if document.note.name == note_name][0])
            #if the note is empty, insert a hashtag to start a heading
            if not self.toPlainText():
                self.insertPlainText("#")
        else:
            raise Exception(f"Document name {note_name} does not exist")

    #checks whether document with note_name is featured in the editors self.note_documents
    def check_in_documents(self, note_name : str):
        if type(note_name) != str:
            raise Exception(f"Invalid note name: {note_name} -- not a string.")
        return note_name in [document.note.name for document in self.note_documents]


    #when the link is clicked, checks if the link is a note reference and then sends the editor there if thats the case
    def check_link(self, link : QUrl):

        link_path = link.path()

        if self.check_in_documents(link_path):
            self.set_note(link_path)
            self.new_note_set_signal.emit(app.user_notes.get(link_path)) #passes the note selected into signal broadcast


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

        network.on("doubleClick", function(eventobj) {
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

    note_selected_signal = pyqtSignal(app.Note) #custom signal emitted to show note was selected

    def __init__(self, note_network : NoteNetwork, debug : bool = False):
        super().__init__()

        self.selected_note = None

        #hides scroll bars
        self.settings().setAttribute(QWebEngineSettings.WebAttribute.ShowScrollBars, False)
        self.note_network = note_network

        #displays loading information if debug is enabled
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
        nodes = eventobj.toObject()["nodes"].toArray()
        #only if the double click featured a node will we count it as a selection
        if nodes:
            node = nodes[0].toString()
            self.selected_note = self.note_network.get_note(node)
            self.note_selected_signal.emit(self.selected_note)

    def render(self):
        self.setHtml(self.note_network.return_html())


class Window(QMainWindow):

    def __init__(self, max_screen_height : int = 1080):
        super().__init__()


        self.tabs = QTabWidget()
        self.tab1 = QWidget()

        self.tab1layout = QVBoxLayout()
        self.tab1layout.setContentsMargins(0, 0, 0, 0)
        self.tab1layout.setSpacing(0)

        self.tab1.setLayout(self.tab1layout)

        self.note_network = NoteNetwork(bg_color=self.palette().window().color().name(), screen_max_height=max_screen_height)
        self.graph = NoteNetworkView(self.note_network, debug=True)

        self.graph.note_selected_signal.connect(self.open_editor)

        self.tab1layout.addWidget(self.graph)

        self.tabs.addTab(self.tab1, "Your Note Network")

        self.setCentralWidget(self.tabs)

    #opens the editor tab and sets it to the correct document, with the document name as tab title
    def open_editor(self, selected_node):

        #creates editor for the note
        self.editor = NoteEditor()
        self.editor.new_note_set_signal.connect(self.open_editor)
        self.editor.set_note(selected_node.name)

        #creates page layout and tab, adding it to tabs
        self.note_tab_layout = QVBoxLayout()
        self.note_tab = QWidget()
        self.note_tab.setLayout(self.note_tab_layout)
        self.note_tab_layout.addWidget(self.editor)
        self.tabs.addTab(self.note_tab, selected_node.name)

        #sets current tab to the note
        self.tabs.setCurrentIndex(self.tabs.indexOf(self.note_tab))


Application = QApplication(sys.argv)
height = Application.primaryScreen().size().height()
window = Window(height)
window.setWindowTitle("pynote!")

window.show()

Application.exec()