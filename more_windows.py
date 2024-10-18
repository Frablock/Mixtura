import sys, os, signal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog, QHBoxLayout, QFrame, QPushButton, QSizePolicy, QTextEdit, QSlider, QComboBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie, QImage

from PIL import Image

class InpaintWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Affichage de la zone à éditer")
        self.setGeometry(200, 200, 300, 200)

        self.setStyleSheet("background-color: #282020;border: 0px solid #ccc;")

        layout = QVBoxLayout()

        self.labelInpaint = QLabel()
        layout.addWidget(self.labelInpaint)

        self.CheckUse = QCheckBox("Utiliser la zone d'édition")
        layout.addWidget(self.CheckUse)
        self.CheckUse.setStyleSheet('''
            QCheckBox {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        self.setLayout(layout)

class OriginalWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image originale")
        self.setGeometry(200, 200, 600, 600)

        self.setStyleSheet("background-color: #282020;border: 0px solid #ccc;")

        layout = QVBoxLayout()

        self.labelInpaint = QLabel()
        layout.addWidget(self.labelInpaint)

        self.setLayout(layout)
    def setPixmap(self, image):
        scaled_pixmap = image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.labelInpaint.setPixmap(scaled_pixmap)
