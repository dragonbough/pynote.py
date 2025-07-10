import sys
import app
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class NoteItem(QTextDocument):
    
    def __init__(self, id : str):
        
        self.note =  app.Note(id)

class Window(QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()
        self.texteditor = QTextEdit()
        self.layout.addWidget(self.texteditor)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
app = QApplication(sys.argv)
window = Window()
window.show()

app.exec()