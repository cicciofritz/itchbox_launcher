from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

import sys

import pygame
from pygame import *


game_list=[]
game_index=0
num_game=0
worker=None
keepPlaying = True

class Signals(QObject):
    close = pyqtSignal(int)

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
                    game_list[game_index].action()
                    #keepPlaying = False
                #print("Joystick button UP released.")

                if event.type == pygame.JOYHATMOTION:
                    i=joysticks[-1].get_hat(0)
                    if i[0] == -1:
                        game_list[game_index].setStyleSheet(game_list[game_index].uncover)
                        game_index = (game_index-1)%(num_game+2)
                        game_list[game_index].setStyleSheet(game_list[game_index].cover)
                    if i[0] == 1:
                        game_list[game_index].setStyleSheet(game_list[game_index].uncover)
                        game_index = (game_index+1)%(num_game+2)
                        game_list[game_index].setStyleSheet(game_list[game_index].cover)

 
class Window(QWidget):
    def __init__(self):
        global num_game, game_list, worker
        super().__init__()
        pool = QThreadPool.globalInstance()
        worker = Worker()
        pool.start(worker)

        self.centralwidget = QWidget()
        grid=QGridLayout(self.centralwidget)
        grid.setRowStretch(0, 1)
        grid.setRowStretch(1, 2)
        grid.setRowStretch(2, 1)

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
        self.label = QLabel(self)
        self.label.setFont(QFont("Sanserif", 10))
        self.label.setStyleSheet("color: white;")
        self.label.setMinimumSize(100, 100) 
        grid.addWidget(self.label, 2, 0,  Qt.AlignLeft)

        for i in range(0,3):
            game = QPushButton("")
            #da sostituire con dati da csv
            if i == 0:
                game.name = "Bloodborne"
                game.cover = "border-image: url(img1.png);"
                game.uncover = "border-image: url(img1_.png);"
                game.command = ""
            elif i==1:
                game.name = "Super Mario"
                game.cover = "border-image: url(img2.png);"
                game.uncover = "border-image: url(img2_.png);"
                game.command = ""
            elif i==2:
                game.name = "Indy Heat"
                game.cover = "border-image: url(img3.png);"
                game.uncover = "border-image: url(img3_.png);"
                game.command = ""
            
            game.index = i
            game.setStyleSheet(game.uncover)
            game.action = self.start_game #(self.label.setText("Avvio di "+ button1.name + "..."), print("Avvio di "+ button1.name + "..."))
            game.clicked.connect(game.action)
            game.installEventFilter(self)
            game.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            game_list.append(game)
            grid.addWidget(game, 1, i)

        num_game=i+1
        #print(str(num_game))

        buttonupd = QPushButton("")
        buttonupd.index = i+1
        buttonupd.cover = "border-image: url(aggiorna.png);"
        buttonupd.uncover = "border-image: url(aggiorna_.png);"
        buttonupd.setStyleSheet(buttonupd.uncover)
        buttonupd.setIconSize(QSize(60, 60))
        buttonupd.action = self.update_game
        buttonupd.clicked.connect(buttonupd.action)
        buttonupd.installEventFilter(self)
        grid.addWidget(buttonupd, 2, 3)
        game_list.append(buttonupd)

        buttonexit = QPushButton("")
        buttonexit.index = i+2
        buttonexit.cover = "border-image: url(spegni128.png);"
        buttonexit.uncover = "border-image: url(spegni128_.png);"
        buttonexit.setStyleSheet(buttonexit.uncover)
        buttonexit.setIconSize(QSize(60, 60))
        buttonexit.action = self.btnexit
        buttonexit.clicked.connect(buttonexit.action)
        buttonexit.action = self.btnexit
        buttonexit.installEventFilter(self)
        grid.addWidget(buttonexit, 2, 4)
        game_list.append(buttonexit)

        self.setLayout(grid)
        self.show()
        #self.showFullScreen()


    def start_game(self):
        #run game_list[game_index].command
        self.label.setText("Avvio di "+ game_list[game_index].name + "...")
        print(game_list[game_index].name)
 
    def btnexit(self):
        global keepPlaying, worker
        keepPlaying = False
        self.label.setText("Spegnimento in corso...")
        worker.signals.close.emit(False)
        self.close()

    def update_game(self):
        global game_list
        self.label.setText("Aggiornamento in corso...")
        game_list=[]
        self.close()
        self.__init__() 

    def keyPressEvent(self, event): 
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def eventFilter(self, object, event):
        global game_index
        if event.type() == QEvent.HoverMove:
            game_list[game_index].setStyleSheet(game_list[game_index].uncover)
            game_index = object.index
            game_list[game_index].setStyleSheet(game_list[game_index].cover)
            return True
        return False

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())