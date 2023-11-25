from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from PIL import Image

import sys, subprocess

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
pathvariable = "data/" 
#pathvariable = "../itchbox/data/"

######## JOYPAD ###########
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
                    self.signals.close.emit(False)
                if event.type == pygame.JOYHATMOTION:
                    i=joysticks[-1].get_hat(0)
                    if i[0] != 0:
                        self.signals.direction.emit(i[0])
        #print("stopper joystick")
        pygame.joystick.quit()
 
######## JOYPAD END ###########

class GameBtn(QPushButton):
    def __init__(self, index, name, image, command, action, event):
        global pathvariable
        super().__init__()
        pathvariable = "data/" #"../itchbox/data/"
        self.index = index
        self.name = name
        self.image = image
        img = Image.open(str(pathvariable + image)).convert('L')
        img.save(str(pathvariable + "_" + image))
        self.cover = str("border-image: url(" + pathvariable + image + ");")
        self.uncover = str("border-image: url(" + pathvariable +"_" + image + ");")
        if (name == "Spegni"):
            self.command = command
        else:
            self.command = str("../itchbox/" + command)
        self.setStyleSheet(self.uncover)
        if (name == "Aggiorna") or (name == "Spegni"):
            self.setIconSize(QSize(60, 60))
        else:
            self.setMinimumHeight(350)
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

class Window(QWidget):
    def __init__(self):
        global num_game, game_list, game_index, worker, maingrid, message, innergrid, pathvariable
        super().__init__()
        
        self.centralwidget = QWidget()
        maingrid=QGridLayout(self.centralwidget)

        oImage = QImage(str(pathvariable + "sfondo.jpg"))
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
        self.setWindowIcon(QIcon(str(pathvariable + "itchbox128.png")))
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Riquadro di testo
        message = TxtLabel()
        maingrid.addWidget(message, 1, 0)

        #scroll area per le caselle con i giochi
        self.innerwidget = QWidget()
        innergrid = QGridLayout() #griglia dei giochi

        num_game=self.parse_csv()

        self.innerwidget.setLayout(innergrid)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.innerwidget)

        maingrid.addWidget(self.scrollArea, 0, 0)
        self.setLayout(maingrid)
        self.installEventFilter(self)

        self.show()
        #self.showFullScreen()

    def start_game(self):
        global message, worker
        
        message.textStart(game_list[game_index])
        print(game_list[game_index].name)
        if game_list[game_index].name == "Spegni":
            message.textStart(self)
            worker.signals.close.emit(False)
            self.centralwidget.close()
            self.close()
            #subprocess.call([game_list[game_index].command], '-1')
        elif game_list[game_index].name == "Aggiorna":
            message.textStart(self)
            #subprocess.call(['sh', game_list[game_index].command])
            self.innerwidget=[] #distruggi elenco attuale
            self.close()
            self.__init__()
        else:
            #subprocess.call(['sh', game_list[game_index].command])
            pass

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
        self.scrollArea.ensureWidgetVisible(game_list[game_index], 50, 50)
        message.textShow(game_list[game_index])

    def parse_csv(self):
        global innergrid, game_index
        file1 = open(str(pathvariable + 'lista.csv'), 'r')
        i = 0

        for line in file1: #crea tutti i pulsanti a partire dal csv, riga 1 e riga 2 riservati a "aggiorna" e "spegni"
            game = GameBtn(i, line.split(',')[0], line.split(',')[2].strip(), line.split(',')[1], self.start_game, self)

            if i == 2:
                game.markObj()
                game_index = 2

            game_list.append(game)
            if game.name == "Aggiorna":
                maingrid.addWidget(game_list[i], 1, 1)#5)
            elif game.name == "Spegni":
                maingrid.addWidget(game_list[i], 1, 2)#6)
            else:
                innergrid.addWidget(game_list[i], int((i-2)/3), int((i-2)%3))
            i += 1

        file1.close()

        return i

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())