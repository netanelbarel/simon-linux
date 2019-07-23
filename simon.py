import os, sys, glob, math, random, time
from PyQt5.QtWidgets import (QMainWindow, QWidget,
                             QGridLayout, QPushButton, QApplication,
                             QAction, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QIcon, QCloseEvent
from PyQt5.QtMultimedia import QSound
from PyQt5 import QtCore

app_dir = '/app/share/simon'
sound_folder = 'sound'
sound_yellow= 'yellow.wav'
sound_red = 'red.wav'
sound_green = 'green.wav'
sound_blue = 'blue.wav'
image_folder = 'img'

class SimonGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.status = {}
        self.cell_width = 300
        self.cell_height = 300
        self.game_list = []
        self.current_index = -1
        self.player = True
        self.initUI()

    def initUI(self):

        self.sounds = {
            'yellow': QSound(os.path.join(app_dir, sound_folder, sound_yellow)),
            'red': QSound(os.path.join(app_dir, sound_folder, sound_red)),
            'green': QSound(os.path.join(app_dir, sound_folder, sound_green)),
            'blue': QSound(os.path.join(app_dir, sound_folder, sound_blue))
        }

        self.gridWidget = QWidget(self)
        self.gridLayout = QGridLayout(self.gridWidget)
        self.setCentralWidget(self.gridWidget)

        self.setGeometry(700, 300, 600, 600)
        self.setWindowTitle('Simon Game!')
        self.showDialog()
        self.show()
        # self.showFullScreen()

    def showDialog(self):
        """Seacrh for a folder of images, and create two dictionaries:
        - one with grid_position : image"""

        self.status = {}
        
        self.list_images(os.path.join(app_dir, 'img'))

		# if the selected foldser contains images, limit the number to 16
        self.fill_dict(self.images)  # create the grid_position:image Dict
        self.init_grid()

    def list_images(self, folder):
        """List the (JPEG) images within the selected folder"""
        extensions = ('.jpg', '.jpeg', '.gif', '.png')
        images = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(extensions)]
        images = sorted(images)
        n_img = len(images)

        self.images = images
        self.n_img = n_img

    def fill_dict(self, images):
        grid_cell = images
        self.card_dict = {}
        n_cols = 2
        n_rows = 2

        positions = [(i, j) for i in range(n_rows) for j in range(n_cols)]
        for p, cell in zip(positions, grid_cell):
            self.card_dict[p] = cell

    def init_grid(self):
        """Initialize the grid according to the number of images
        found in the selected folder."""

        for pos, img in self.card_dict.items():
            btn = QPushButton(self)
            btn.clicked.connect(self.buttonClicked)
            pixmap = QPixmap(img)
            scaled = pixmap.scaled(self.cell_width, self.cell_height)
            btn.setIcon(QIcon(scaled))
            btn.setIconSize(scaled.rect().size())
            btn.setFixedSize(scaled.rect().size())
            del (pixmap)

            self.gridLayout.addWidget(btn, *pos)

    def restart(self):
        self.game_list = []
        self.current_index = -1
        self.player = True
        self.play_game()
        return

    def play_card(self, btn, location):
        """When a button (image) is clicked, turn the card."""

        pixmap = QPixmap(self.card_dict[location])
        scaled = pixmap.scaled(self.cell_width - 30 , self.cell_height - 30)
        btn.setIcon(QIcon(scaled))
        btn.setIconSize(scaled.rect().size())
        btn.setFixedSize(scaled.rect().size())

        color = self.card_dict[location].split('/')[-1].split('.')[0]

        self.sounds[color].play()

        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(100, loop.quit)
        loop.exec_()

        scaled = pixmap.scaled(self.cell_width , self.cell_height)
        btn.setIcon(QIcon(scaled))
        btn.setIconSize(scaled.rect().size())
        btn.setFixedSize(scaled.rect().size())

        del (pixmap)
        return

    def buttonClicked(self):
        if self.player:
            button = self.sender()
            idx = self.gridLayout.indexOf(button)
            location = self.gridLayout.getItemPosition(idx)
            self.play_card(button, location[:2])
            self.current_index += 1
            if idx != self.game_list[self.current_index]:
                self.end_game()
            elif self.current_index == len(self.game_list) - 1:
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(200, loop.quit)
                loop.exec_()
                self.play_game()

    def play_game(self):
        if self.current_index == len(self.game_list) - 1:
            self.player = False
            r_index = random.randint(0, 3)
            self.game_list.append(r_index)
            print(self.game_list)
            for index in self.game_list:
                button = self.gridLayout.itemAt(index).widget()
                idx = self.gridLayout.indexOf(button)
                location = self.gridLayout.getItemPosition(idx)
                self.play_card(button, location[:2])
                loop = QtCore.QEventLoop()
                QtCore.QTimer.singleShot(200, loop.quit)
                loop.exec_()
            self.player = True
            self.current_index = -1
            
    def end_game(self):

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setWindowTitle("Game Over")
        msgBox.setInformativeText("אופססס! טעית אחרי {} תווים\nרוצה להמשיך למשחק הבא ?".format(len(self.game_list)))
        quit = msgBox.addButton('quit', QMessageBox.RejectRole)
        restartBtn = msgBox.addButton('play again', QMessageBox.ActionRole)
        msgBox.setDefaultButton(restartBtn)

        msgBox.exec_()
        msgBox.deleteLater()

        if msgBox.clickedButton() == quit:
            self.close()
        elif msgBox.clickedButton() == restartBtn:
            self.restart()

        return

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimonGame()
    loop = QtCore.QEventLoop()
    QtCore.QTimer.singleShot(1000, loop.quit)
    loop.exec_()
    ex.play_game()
    sys.exit(app.exec_())