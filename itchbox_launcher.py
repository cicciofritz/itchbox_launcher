from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import *

import pygame, sys, subprocess, datetime, pickle

worker=None

#impostare il percorso relativo della cartella data
datapath = "../itchbox/data/"
gamepath = "../itchbox/"

#bypass_call se True non esegue gli script sh (lancia gioco, update, disinstalla, spegni)
bypass_call = False

#dati di gioco
playtime = {}

######## JOYPAD ###########
class Signals(QObject):
    close = pyqtSignal(int)
    direction = pyqtSignal(int, int)
    launch = pyqtSignal(int)
    delete = pyqtSignal(int)

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

                    if event.type == pygame.JOYBUTTONDOWN:
                        if joysticks[-1].get_button(3) == True: #triangolo
                            print("premuto triangolo")
                            self.signals.delete.emit(1)
                            self.signals.close.emit(False)
                        elif joysticks[-1].get_button(0) == True: #x
                            print("premuto x")
                            self.signals.launch.emit(1)
                            self.signals.close.emit(False)
                    if event.type == pygame.JOYHATMOTION:
                        i=joysticks[-1].get_hat(0)
                        if i[0] != 0 or i[1] != 0:
                            self.signals.direction.emit(i[0], i[1])
            except:
                print("Oops")
        pygame.joystick.quit()
 
######## JOYPAD END ###########

class GameBtn(QPushButton):
    def __init__(self, index, name, image, command, action, event):
        global datapath
        super().__init__()
        self.index = index
        self.name = name
        self.setStyleSheet(str("border-image: url(" + datapath + image + ");"))
        self.unmarkObj()
        self.command = command
        if (name == "Aggiorna") or (name == "Spegni"):
            self.setMinimumSize(80, 80)
            self.setMaximumSize(80, 80)
        else:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            h=self.frameGeometry().height()
            self.setMinimumSize(int(h*315/250), h) #riscalo cercando di mantenere le proporzioni
        self.clicked.connect(action)
        self.installEventFilter(event)
        #prova per tempo di gioco
        self.time_flag=0
        self.start_time=0
        if self.name in playtime:
            self.total_time=playtime[self.name]
        else:
            self.total_time=datetime.timedelta(0) #playtime[self.name]

    def markObj(self):
        self.setGraphicsEffect(None)

    def unmarkObj(self):        
        effect = QGraphicsColorizeEffect()
        effect.setColor(QColor(Qt.gray))
        effect.setStrength(1)
        self.setGraphicsEffect(effect)

class TxtLabel(QLabel):
    def __init__(self):
        super().__init__()
        self.setFont(QFont("Sanserif", 15))
        self.setStyleSheet("color: white;")
        self.setMinimumSize(100, 100)

    def textStart(self, object):
        if object.name == "Spegni":
            self.setText("Spegnimento in corso...")
        elif object.name == "Aggiorna":
            self.setText("Aggiornamento in corso...")
        else:
            self.setText("Avvio di "+ object.name + "...")
            
    def textShow(self, object):
        self.setText(object.name)

class Window(QWidget):
    def __init__(self):
        global worker, datapath, playtime
        super().__init__()
        
        #carica dati di gioco
        try:
            fileObj = open('data.obj', 'rb')
            playtime = pickle.load(fileObj)
            fileObj.close()
        except:
            pass

        self.centralwidget = QWidget()
        self.maingrid = QGridLayout(self.centralwidget)

        #sfondo principale
        oImage = QImage(str(datapath + "sfondo.jpg"))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(oImage))                        
        self.setPalette(palette)

        #proprietà finestra principale
        self.title = "itchbox"
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon(str(datapath + "itchbox128.png")))
        self.setGeometry(500, 200, 600, 400) #almost useless in fullscreenmode

        #creo e popolo un widget con i giochi
        self.innerwidget = QWidget()
        self.innergrid = QGridLayout() #griglia dei giochi
        self.game_list = []
        self.game_index = 2
        try:
            self.num_game=self.parse_csv() #leggo lista giochi dal csv e li aggiungo al widget
        except:
            print("Errore nella lettura del csv")
        self.innerwidget.setLayout(self.innergrid)

        #inserisco l'elenco dei giochi a una zona scrollabile verticalmente
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background: transparent")
        self.scrollArea.setWidget(self.innerwidget)

        #riquadro giochi disponibili nella finestra principale
        self.maingrid.addWidget(self.scrollArea, 1, 0, 1, 3)
        self.setLayout(self.maingrid)
        
        #riquadro di testo nella finestra principale
        self.message = TxtLabel()
        self.maingrid.addWidget(self.message, 2, 0)

        self.time = TxtLabel()
        self.maingrid.addWidget(self.time, 2, 1, Qt.AlignRight)

        self.titlewidget = QWidget()
        self.titlegrid = QGridLayout()
        self.systxt = TxtLabel()
        self.systxt.setFont(QFont('Arial', 15, QFont.Bold))
        self.systxt.setText("Loading...")
        self.titlegrid.addWidget(self.systxt, 0, 1, 2, 1, Qt.AlignRight)
        self.titlewidget.setLayout(self.titlegrid)
        
        # Configure font and color for the digital clock display
        self.timetxt = TxtLabel()
        self.timetxt.setFont(QFont('Arial', 60, QFont.Bold))
        self.timetxt.setStyleSheet("color: white;")

        self.datetxt = TxtLabel()
        self.datetxt.setFont(QFont('Arial', 20, QFont.Bold))
        self.datetxt.setStyleSheet("color: white;")
        
        # Format and display the current time
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateTime)
        self.timer.start(1000)  # Update every 1000 milliseconds (1 second)
        self.current_time = QTime.currentTime()
        self.timetxt.setText(self.current_time.toString('hh:mm:ss'))
        self.current_date = QDate.currentDate()
        self.datetxt.setText(self.current_date.toString('dddd dd MMMM yy'))
        self.titlegrid.addWidget(self.timetxt, 0, 0, Qt.AlignLeft)
        self.titlegrid.addWidget(self.datetxt, 1, 0, Qt.AlignLeft)
        self.maingrid.addWidget(self.titlewidget, 0, 0, 1, 4)

        #aggancio il filtro eventi eventFilter alla finestra principale
        self.installEventFilter(self)

        self.show()
        self.showFullScreen()

    def updateTime(self):
        self.current_time = QTime.currentTime()
        self.current_date = QDate.currentDate()
        time_str = self.current_time.toString('hh:mm:ss')
        self.timetxt.setText(time_str)
        date_str = self.current_date.toString('dddd dd MMMM yy')
        self.datetxt.setText(date_str)
        if bypass_call == False:
            self.systxt.setText(subprocess.check_output(['sh', '../itchbox/info.sh']).decode('ascii'))

    def start_game(self):
        global worker, bypass_call, playtime, gamepath
        
        self.message.textStart(self.currentGet())
        print(self.currentGet().name)
        if self.currentGet().name == "Spegni":
            #salvo dati di gioco
            fileObj = open('data.obj', 'wb')
            pickle.dump(playtime,fileObj)
            fileObj.close()

            worker.signals.close.emit(False)
            pygame.time.wait(1000) #ritardo per chiudere in maniera pulita il pygame environment
            self.centralwidget.close()
            self.close()
            if bypass_call == False:
                #subprocess.call([self.currentGet().command])
                pass
        elif self.currentGet().name == "Aggiorna":
            if bypass_call == False:
                subprocess.call(['sh', self.currentGet().command])
            self.innerwidget=[] #distruggi elenco attuale
            self.close()
            self.__init__() #reload windows with new csv file
        else:
            self.currentGet().start_time = datetime.datetime.now()
            self.currentGet().time_flag = 1
            if bypass_call == False:
                subprocess.call(['sh', gamepath + self.currentGet().command])

    def delete_game(self):
        global worker, bypass_call

        if bypass_call == False:
            subprocess.call(['sh', self.currentGet().uninstall])
        self.innerwidget=[] #distruggi elenco attuale
        self.close()
        self.__init__() #reload windows with new csv file


    def keyPressEvent(self, event): 
        if event.key() == Qt.Key_F11:
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

    #gestore eventi
    def eventFilter(self, object, event):
        global worker, playtime
        if event.type() == QEvent.HoverMove: #utile solo se si usa il mouse
            self.currentGet().unmarkObj()
            self.game_index = object.index
            self.currentGet().markObj()
            self.message.textShow(self.currentGet())
            self.time.setText("Giocato per " + str(self.currentGet().total_time))
            return True
        if event.type() == QEvent.FocusIn: #necessario per riattivare l'uso del gamepad dopo aver chiuso un gioco
            self.pool = QThreadPool.globalInstance()
            worker = Worker()
            self.pool.start(worker)
            worker.signals.direction.connect(self.navigation)
            worker.signals.launch.connect(self.start_game)
            worker.signals.delete.connect(self.delete_game)
            end_time = datetime.datetime.now()
            if self.currentGet().time_flag != 0:
                self.currentGet().total_time += (end_time - self.currentGet().start_time)
                playtime[self.currentGet().name] = self.currentGet().total_time
                self.currentGet().time_flag = 0
            return True
        if event.type() == QEvent.FocusOut: #necessario per spegnere l'uso del gamepad quando il launcher non è in primo piano
            worker.signals.close.emit(False)
            return True
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.RightButton:
                print("Right button clicked")
        return False

    def navigation(self, direction, mode):
        self.currentGet().unmarkObj()
        self.game_index = (self.game_index + direction)%(self.num_game)
        if mode != 0:
            if self.game_index > 1:
                self.game_index = 0
            else:
                self.game_index = 2
        self.currentGet().markObj()
        self.scrollArea.ensureWidgetVisible(self.currentGet(), 50, 50) #serve a centrare la scrollarea sul gioco selezionato
        self.message.textShow(self.currentGet())
        self.time.setText("Giocato per: " + str(self.currentGet().total_time))

    #funzione principale per lettura file e creazione pulsanti di gioco + aggiorna e spegni
    def parse_csv(self):
        file1 = open(str(datapath + 'lista.csv'), 'r')
        i = 0
        self.game_index = 0

        for line in file1: #crea tutti i pulsanti a partire dal csv, riga 1 e riga 2 riservati a "aggiorna" e "spegni"
            game = GameBtn(i, line.split(',')[0], line.split(',')[2].strip(), line.split(',')[1], self.start_game, self)

            if i == 2:
                game.markObj()
                self.game_index = 2

            self.game_list.append(game)
            if game.name == "Aggiorna":
                self.maingrid.addWidget(self.game_list[i], 2, 2)
            elif game.name == "Spegni":
                self.maingrid.addWidget(self.game_list[i], 2, 3)
            else:
                self.innergrid.addWidget(self.game_list[i], 1, i-2)
            i += 1

        file1.close()

        return i
    
    def currentGet(self):
        return self.game_list[self.game_index]


if __name__ == "__main__":
    App = QApplication(sys.argv)
    window = Window()

    sys.exit(App.exec())