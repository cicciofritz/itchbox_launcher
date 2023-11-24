from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from itchbox_class import *

import sys

import pygame
from pygame import *

game_list=[]
game_index=0
message=0
num_game=0
worker=None
keepPlaying = True
maingrid=None
innergrid=None

class Signals(QObject):
    close = pyqtSignal(int)
    direction = pyqtSignal(int)
    launch = pyqtSignal(int)

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
        global keepPlaying
        joystick_present = False
        keepPlaying = True
        pygame.init()
        clock = pygame.time.Clock()
        joysticks = []

        for i in range(0, pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))
            joysticks[-1].init()
            print ("Detected joystick " + joysticks[-1].get_name())
            joystick_present=True
        while keepPlaying and joystick_present:
            clock.tick(20)
            for event in pygame.event.get():
                if event.type == pygame.JOYBUTTONUP:
                    self.signals.launch.emit(1)
                    #keepPlaying = False
                if event.type == pygame.JOYHATMOTION:
                    i=joysticks[-1].get_hat(0)
                    if i[0] != 0:
                        self.signals.direction.emit(i[0])
        pygame.joystick.quit()
 
class Window(QWidget):
    def __init__(self):
        global num_game, game_list, worker, maingrid, message, innergrid
        super().__init__()

        self.centralwidget = QWidget()
        maingrid=QGridLayout(self.centralwidget)

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
        message = TxtLabel()
        maingrid.addWidget(message, 1, 0)

        #scroll area per le caselle con i giochi
        self.innerwidget = QWidget()
        innergrid=QGridLayout(self.innerwidget)
        scrollArea = QScrollArea()
        scrollArea.setWidget(self.innerwidget)
        maingrid.addWidget(scrollArea, 0, 0)

        num_game=self.parse_csv()

        self.innerwidget.setMinimumSize(600,1000)
        scrollArea.setLayout(innergrid)
        self.setLayout(maingrid)
        
        self.show()
        self.innerwidget.show()

        #self.showFullScreen()

    def start_game(self):
        global message
        #run game_list[game_index].command
        message.textStart(game_list[game_index])
        print(game_list[game_index].name)
 
    def btnexit(self):
        global worker, message
        message.textStart(self)
        worker.signals.close.emit(False)
        self.innerwidget.close()
        self.close()

    def update_game(self):
        global game_list, message
        message.textStart(self)
        self.close()
        self.__init__() 

    def keyPressEvent(self, event): 
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    def eventFilter(self, object, event):
        global game_index, game_list, worker
        if event.type() == QEvent.HoverMove:
            game_list[game_index].unmarkObj()
            game_index = object.index
            game_list[game_index].markObj()
            message.textShow(game_list[game_index])
            return True
        if event.type() == QEvent.FocusIn:
            self.pool = QThreadPool.globalInstance()
            worker = Worker()
            self.pool.start(worker)
            worker.signals.direction.connect(self.navigation)
            worker.signals.launch.connect(self.start_game)
            return True
        if event.type() == QEvent.FocusOut:
            worker.signals.close.emit(False)
            return True
        return False

    def navigation(self, direction):
        global game_index, game_list
        game_list[game_index].unmarkObj()
        game_index = (game_index + direction)%(num_game)
        game_list[game_index].markObj()
        message.textShow(game_list[game_index])

    def parse_csv(self):
        global innergrid
        file1 = open('lista.csv', 'r')
        i = 0

        for line in file1:
            game = GameBtn(i, line.split(',')[0], line.split(',')[2].strip(), line.split(',')[1], self.start_game, self)

            if i == 0:
                game.markObj()

            game_list.append(game)
            innergrid.addWidget(game_list[i], int(i/3), int(i%3))
            i += 1

        file1.close()

        game_list.append(UpdateBtn(i, self.update_game, self))
        maingrid.addWidget(game_list[i], 1, 5)
        
        i += 1

        game_list.append(ExitBtn(i, self.btnexit, self))
        maingrid.addWidget(game_list[i], 1, 6)
        
        i += 1

        return i

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())