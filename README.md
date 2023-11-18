# itchbox_launcher

Interfaccia per itchbox [carlominucci/itchbox](https://github.com/carlominucci/itchbox/tree/main) scritta in PyQt5.

Versione embrionale in sviluppo, scritta da un novellino principiante. Se ne sconsiglia l'utilizzo.

Richiede python3, PyQt5 e pygame
* sudo apt install python3
* sudo apt install python3-pip
* pip install PyQt5
* pip install pygame

Eseguire python3 itchbox_launcher.py
Per comodità si apre in modalità finestra.

Bug noti: in presenza di Gamepad è necessario killare il processo dopo aver chiuso la finestra (c'è un loop bloccante per la lettura gestito male)
