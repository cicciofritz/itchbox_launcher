from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

from PIL import Image
import sys

class GameBtn(QPushButton):
    def __init__(self, index, name, image, command, action, event):
        super().__init__()
        pathvariable = "data/" #"../itchbox/data/"
        self.index = index
        self.name = name
        self.image = image
        img = Image.open(str(pathvariable + image)).convert('L')
        img.save(str(pathvariable + "_" + image))
        self.cover = str("border-image: url(" + pathvariable + image + ");")
        self.uncover = str("border-image: url(" + pathvariable +"_" + image + ");")
        self.command = str("../itchbox/" + command)
        self.setStyleSheet(self.uncover)
        if (name == "Aggiorna") or (name == "Spegni"):
            self.setIconSize(QSize(60, 60))
        else:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.action = action
        self.clicked.connect(self.action)
        self.installEventFilter(event)

    def markObj(self):
        self.setStyleSheet(self.cover)

    def unmarkObj(self):
        self.setStyleSheet(self.uncover)

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
        
