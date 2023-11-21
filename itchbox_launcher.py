from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

import sys
import urllib.request
import re

import pygame
from pygame import *

from PIL import Image

game_list=[]
game_index=0
message=0
num_game=0
worker=None
keepPlaying = True
grid=None

class Signals(QObject):
    close = pyqtSignal(int)
    direction = pyqtSignal(int)
    launch = pyqtSignal(int)

class GameObj(QPushButton):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.name = ""
        self.image = ""
        self.cover = ""
        self.uncover = ""
        self.command = ""
        self.action = None

class Worker(QRunnable):
    def __init__(self):
        super().__init__()
        self.signals = Signals()
        self.signals.close.connect(self.update)

    def update(self):
        global keepPlaying
        keepPlaying = False

    @pyqtSlot()
    def run(self):
        global keepPlaying, game_list, game_index
        joystick_preset = False
        pygame.init()
        clock = pygame.time.Clock()
        joysticks = []
    # for al the connected joysticks
        for i in range(0, pygame.joystick.get_count()):
        # create an Joystick object in our list
            joysticks.append(pygame.joystick.Joystick(i))
        # initialize the appended joystick (-1 means last array item)
            joysticks[-1].init()
        # print a statement telling what the name of the controller is
            print ("Detected joystick " + joysticks[-1].get_name())
            joystick_preset=True
        while keepPlaying and joystick_preset:
            clock.tick(20)
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONUP:
                    self.signals.launch.emit(1)
                    #keepPlaying = False

                if event.type == pygame.JOYHATMOTION:
                    i=joysticks[-1].get_hat(0)
                    if i[0] != 0:
                        self.signals.direction.emit(i[0])

 
class Window(QWidget):
    def __init__(self):
        global num_game, game_list, worker, grid, message
        super().__init__()
        pool = QThreadPool.globalInstance()
        worker = Worker()
        pool.start(worker)
        worker.signals.direction.connect(self.navigation)
        worker.signals.launch.connect(self.start_game)

        self.centralwidget = QWidget()
        grid=QGridLayout(self.centralwidget)
        #grid.setRowStretch(0, 1)
        #grid.setRowStretch(1, 2)
        #grid.setRowStretch(2, 1)

        oImage = QImage("sfondo.jpg")
        #sImage = oImage.scaledToWidth(self.frameGeometry().width())                   # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))                        
        self.setPalette(palette)
        #self.setStyleSheet("border-image: url(sfondo.jpg);")

        self.title = "itchbox"
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300
        self.setWindowTitle(self.title)
        self.setObjectName('MainWindow')
        self.setWindowIcon(QIcon("itchbox128.png"))
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Riquadro di testo
        message = QLabel(self)
        message.setFont(QFont("Sanserif", 10))
        message.setStyleSheet("color: white;")
        message.setMinimumSize(100, 100) 

        grid.addWidget(message, 2, 0,  Qt.AlignLeft)

        num_game=self.parse_csv()

        buttonupd = GameObj()
        buttonupd.index = num_game
        buttonupd.cover = "border-image: url(aggiorna.png);"
        buttonupd.uncover = "border-image: url(aggiorna_.png);"
        buttonupd.setStyleSheet(buttonupd.uncover)
        buttonupd.setIconSize(QSize(60, 60))
        buttonupd.action = self.update_game
        buttonupd.clicked.connect(buttonupd.action)
        buttonupd.installEventFilter(self)
        grid.addWidget(buttonupd, 2, 5)
        game_list.append(buttonupd)

        buttonexit = GameObj()
        buttonexit.index = num_game+1
        buttonexit.cover = "border-image: url(spegni128.png);"
        buttonexit.uncover = "border-image: url(spegni128_.png);"
        buttonexit.setStyleSheet(buttonexit.uncover)
        buttonexit.setIconSize(QSize(60, 60))
        buttonexit.action = self.btnexit
        buttonexit.clicked.connect(buttonexit.action)
        buttonexit.action = self.btnexit
        buttonexit.installEventFilter(self)
        grid.addWidget(buttonexit, 2, 6)
        game_list.append(buttonexit)

        self.setLayout(grid)
        self.show()
        #self.showFullScreen()

    def start_game(self):
        global message
        #run game_list[game_index].command
        message.setText("Avvio di "+ game_list[game_index].name + "...")
        print(game_list[game_index].name)
 
    def btnexit(self):
        global keepPlaying, worker, message
        keepPlaying = False
        message.setText("Spegnimento in corso...")
        worker.signals.close.emit(False)
        self.close()

    def update_game(self):
        global game_list, message
        message.setText("Aggiornamento in corso...")
        self.close()
        self.__init__() 

    def keyPressEvent(self, event): 
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def eventFilter(self, object, event):
        global game_index, game_list
        if event.type() == QEvent.HoverMove:
            game_list[game_index].setStyleSheet(game_list[game_index].uncover)
            game_index = object.index
            game_list[game_index].setStyleSheet(game_list[game_index].cover)
            message.setText(game_list[game_index].name)
            return True
        return False

    def navigation(self, direction):
        global game_index, game_list
        game_list[game_index].setStyleSheet(game_list[game_index].uncover)
        game_index = (game_index + direction)%(num_game+2)
        game_list[game_index].setStyleSheet(game_list[game_index].cover)
        message.setText(game_list[game_index].name)

    def parse_csv(self):
        file1 = open('lista.csv', 'r')
        i = 0

        for line in file1:
            game = GameObj()
            game.name = line.split(',')[0]
            game.index = i
            game.image = self.retrieveCover(game.name)
            game.cover = str("border-image: url(data/" + game.image + ");")
            game.uncover = str("border-image: url(data/_" + game.image + ");")
            game.command = line.split(',')[1]
            game.setStyleSheet(game.uncover)
            game.action = self.start_game
            game.clicked.connect(game.action)
            game.installEventFilter(self)
            game.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            game_list.append(game)
            grid.addWidget(game_list[i], int(i/4), int(i%4))
            i += 1

        file1.close()
        return i

    def retrieveCover(self, name):
        try:
            name_plus = re.sub('( )', '+', name, 0, re.MULTILINE)
            name_plus = str("https://itch.io/search?q=" + name_plus + "\"")
            contents = urllib.request.urlopen(name_plus).read()
            x = re.search("(?<=data-lazy_src=\")(.*?)(?=\")", str(contents)).group()
            name_under = re.sub('( )', '_', name, 0, re.MULTILINE)
            image_name=str( name_under + "." + x.split(".")[-1])

            urllib.request.urlretrieve(x, str("data/" + image_name))
            img = Image.open(str("data/" + image_name)).convert('L')
            img.save(str("data/_" + image_name))
        except:
            image_name = "empty"
        return image_name

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())