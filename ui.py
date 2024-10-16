#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 17 00:25:50 2024

@author: François
"""

import sys, os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie

import transf  # Assurez-vous que ce module existe et qu'il a la fonction transform

# Make sure the path to the GIF is correct
LOADING_IMAGE = os.path.join(os.path.dirname(__file__), "reload-cat.gif")

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Déposez l\'image ici ou cliquez pour la téléverser \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')
        self.movie = None  # This will hold the loading animation

    def setLoadingAnimation(self):
        # Load and show the GIF animation
        if os.path.exists(LOADING_IMAGE):  # Check if the file exists
            self.movie = QMovie(LOADING_IMAGE)
            self.setMovie(self.movie)
            self.movie.start()
            self.repaint()
        else:
            print(f"Error: Loading GIF not found at {LOADING_IMAGE}")

    def clearLoadingAnimation(self):
        # Stop and remove the GIF animation
        if self.movie is not None:
            self.movie.stop()
        self.setMovie(None)  # Clear the movie

    def setPixmap(self, image):
        # Clear the animation before setting a new image
        self.clearLoadingAnimation()
        super().setPixmap(image)

    def mousePressEvent(self, event):
        # Open file dialog when the label is clicked
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(self, "Choisissez une image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
            if file_path:
                self.setLoadingAnimation()  # Show the loading animation
                new_f = self.transform_image(file_path)  # Transform the image
                self.setPixmap(QPixmap(new_f))  # Display the transformed image

    def transform_image(self, file_path):
        # Create the 'outputs' directory if it doesn't exist
        if not os.path.exists("./outputs"):
            os.makedirs("./outputs")

        # Apply the transformation using your custom module
        new_f = "./outputs/" + os.path.basename(file_path)
        transf.transform(file_path, new_f)
        return new_f


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        self.setAcceptDrops(True)

        mainLayout = QVBoxLayout()
        self.photoViewer = ImageLabel()
        mainLayout.addWidget(self.photoViewer)
        self.setLayout(mainLayout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.photoViewer.setLoadingAnimation()  # Show loading animation
        new_f = self.photoViewer.transform_image(file_path)  # Transform the image
        self.photoViewer.setPixmap(QPixmap(new_f))  # Display the transformed image


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = App()
    demo.show()
    sys.exit(app.exec_())
