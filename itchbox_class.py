from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

from PIL import Image
import sys

class ItchboxObj(QPushButton):
    def __init__(self, index, event):
        super().__init__()
        self.index = index
        self.name = ""
        self.image = ""
        self.cover = ""
        self.uncover = ""
        self.command = ""
        self.action = None
        self.installEventFilter(event)
         
    def markObj(self):
        self.setStyleSheet(self.cover)

    def unmarkObj(self):
        self.setStyleSheet(self.uncover)

class GameBtn(ItchboxObj):
    def __init__(self, index, name, image, command, action, event):
        super().__init__(index, event)
        self.name = name
        self.image = image
        img = Image.open(str("data/" + image)).convert('L')
        img.save(str("data/_" + image))
        self.cover = str("border-image: url(data/" + image + ");")
        self.uncover = str("border-image: url(data/_" + image + ");")
        self.command = command
        self.action = action
        self.clicked.connect(self.action)
        self.setStyleSheet(self.uncover)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

class UpdateBtn(ItchboxObj):
    def __init__(self, index, action, event):
        super().__init__(index, event)
        self.name = "Aggiorna"
        self.image = "aggiorna.png"
        self.cover = "border-image: url(aggiorna.png);"
        self.uncover = "border-image: url(aggiorna_.png);"
        self.action = action
        self.clicked.connect(self.action)
        self.setStyleSheet(self.uncover)
        self.setIconSize(QSize(60, 60))

class ExitBtn(ItchboxObj):
    def __init__(self, index, action, event):
        super().__init__(index, event)
        self.name = "Spegni"
        self.image = "spegni128.png"
        self.cover = "border-image: url(spegni128.png);"
        self.uncover = "border-image: url(spegni128_.png);"
        self.action = action
        self.clicked.connect(self.action)
        self.setStyleSheet(self.uncover)
        self.setIconSize(QSize(60, 60))

class TxtLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Sanserif", 10))
        self.setStyleSheet("color: white;")
        self.setMinimumSize(100, 100)

    def textStart(self, object):
        if type(object).__name__ == "GameBtn":
            self.setText("Avvio di "+ object.name + "...")
        elif type(object).__name__ == "ExitBtn":
            self.setText("Spegnimento in corso...")
        elif type(object).__name__ == "UpdateBtn":
            self.setText("Aggiornamento in corso...")
    def textShow(self, object):
        self.setText(object.name)
        
