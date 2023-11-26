from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *
from PIL import Image

import sys, subprocess

import pygame
from pygame import *

worker=None
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
        self.keepPlaying=True

    def update(self):
        self.keepPlaying = False

    @pyqtSlot()
    def run(self):
        joystick_present = False
        pygame.init()
        clock = pygame.time.Clock()
        joysticks = []

        for i in range(0, pygame.joystick.get_count()):
            joysticks.append(pygame.joystick.Joystick(i))
            joysticks[-1].init()
            print ("Detected joystick " + joysticks[-1].get_name())
            joystick_present=True
        while self.keepPlaying and joystick_present:
            clock.tick(20)
            try:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONUP:
                        self.signals.launch.emit(1)
                        self.signals.close.emit(False)
                    if event.type == pygame.JOYHATMOTION:
                        i=joysticks[-1].get_hat(0)
                        if i[0] != 0:
                            self.signals.direction.emit(i[0])
            except:
                print("Oops")
        pygame.joystick.quit()
 
######## JOYPAD END ###########

class GameBtn(QPushButton):
    def __init__(self, index, name, image, command, action, event):
        global pathvariable
        super().__init__()
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
        global worker, pathvariable
        super().__init__()
        
        self.centralwidget = QWidget()
        self.maingrid = QGridLayout(self.centralwidget)

        #sfondo principale
        oImage = QImage(str(pathvariable + "sfondo.jpg"))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))                        
        self.setPalette(palette)

        #proprietà finestra principale
        self.title = "itchbox"
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(str(pathvariable + "itchbox128.png")))
        self.setGeometry(500, 200, 600, 400) #almost useless in fullscreenmode

        #creo e popolo un widget con i giochi
        self.innerwidget = QWidget()
        self.innergrid = QGridLayout() #griglia dei giochi
        self.game_list = []
        self.game_index = 2
        self.num_game=self.parse_csv() #leggo lista giochi dal csv e li aggiungo al widget
        self.innerwidget.setLayout(self.innergrid)

        #inserisco l'elenco dei giochi a una zona scrollabile verticalmente
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.innerwidget)

        #riquadro giochi disponibili nella finestra principale
        self.maingrid.addWidget(self.scrollArea, 0, 0)
        self.setLayout(self.maingrid)
        
        #riquadro di testo nella finestra principale
        self.message = TxtLabel()
        self.maingrid.addWidget(self.message, 1, 0)

        #aggancio il filtro eventi eventFilter alla finestra principale
        self.installEventFilter(self)

        self.show()
        #self.showFullScreen()

    def start_game(self):
        global worker
        
        self.message.textStart(self.game_list[self.game_index])
        print(self.game_list[self.game_index].name)
        if self.game_list[self.game_index].name == "Spegni":
            self.message.textStart(self)
            worker.signals.close.emit(False)
            time.wait(1000) #ritardo per chiudere in maniera pulita il pygame environment
            self.centralwidget.close()
            self.close()
            #subprocess.call([self.game_list[self.game_index].command], '-1')
        elif self.game_list[self.game_index].name == "Aggiorna":
            self.message.textStart(self)
            #subprocess.call(['sh', self.game_list[self.game_index].command])
            self.innerwidget=[] #distruggi elenco attuale
            self.close()
            self.__init__()
        else:
            #subprocess.call(['sh', self.game_list[self.game_index].command])
            pass

    def keyPressEvent(self, event): 
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    #gestore eventi
    def eventFilter(self, object, event):
        global worker
        if event.type() == QEvent.HoverMove: #utile solo se si usa il mouse
            self.game_list[self.game_index].unmarkObj()
            self.game_index = object.index
            self.game_list[self.game_index].markObj()
            self.message.textShow(self.game_list[self.game_index])
            return True
        if event.type() == QEvent.FocusIn: #necessario per riattivare l'uso del gamepad dopo aver chiuso un gioco
            self.pool = QThreadPool.globalInstance()
            worker = Worker()
            self.pool.start(worker)
            worker.signals.direction.connect(self.navigation)
            worker.signals.launch.connect(self.start_game)
            return True
        if event.type() == QEvent.FocusOut: #necessario per spegnere l'uso del gamepad quando il launcher non è in primo piano
            worker.signals.close.emit(False)
            return True
        return False

    def navigation(self, direction):
        self.game_list[self.game_index].unmarkObj()
        self.game_index = (self.game_index + direction)%(self.num_game)
        self.game_list[self.game_index].markObj()
        self.scrollArea.ensureWidgetVisible(self.game_list[self.game_index], 50, 50) #serve a centrare la scrollarea sul gioco selezionato
        self.message.textShow(self.game_list[self.game_index])

    #funzione principale per lettura file e creazione pulsanti di gioco + aggiorna e spegni
    def parse_csv(self):
        file1 = open(str(pathvariable + 'lista.csv'), 'r')
        i = 0

        for line in file1: #crea tutti i pulsanti a partire dal csv, riga 1 e riga 2 riservati a "aggiorna" e "spegni"
            game = GameBtn(i, line.split(',')[0], line.split(',')[2].strip(), line.split(',')[1], self.start_game, self)

            if i == 2:
                game.markObj()

            self.game_list.append(game)
            if game.name == "Aggiorna":
                self.maingrid.addWidget(self.game_list[i], 1, 1)#5)
            elif game.name == "Spegni":
                self.maingrid.addWidget(self.game_list[i], 1, 2)#6)
            else:
                self.innergrid.addWidget(self.game_list[i], int((i-2)/3), int((i-2)%3))
            i += 1

        file1.close()

        return i

if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())