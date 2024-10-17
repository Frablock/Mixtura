import sys, os, signal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog, QHBoxLayout, QFrame, QPushButton, QSizePolicy, QTextEdit, QSlider, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie

import transf  # Make sure this module exists and works properly

LOADING_IMAGE = os.path.join(os.path.dirname(__file__), "reload-cat.gif")
signal.signal(signal.SIGINT, signal.SIG_DFL) # Support du CTRL+C

class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Déposez l\'image ici ou cliquez pour la téléverser \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #d62828
            }
        ''')
        self.movie = None  # To hold the loading animation

    def setLoadingAnimation(self):
        if os.path.exists(LOADING_IMAGE):
            self.movie = QMovie(LOADING_IMAGE)
            self.setMovie(self.movie)
            self.movie.start()
            self.repaint()
        else:
            print(f"Error: Loading GIF not found at {LOADING_IMAGE}")

    def clearLoadingAnimation(self):
        if self.movie is not None:
            self.movie.stop()
        self.setMovie(None)

    def setPixmap(self, image):
        self.clearLoadingAnimation()
        super().setPixmap(image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(self, "Choisissez une image", "", "Images (*.png *.xpm *.jpg *.jpeg *.bmp)")
            if file_path:
                self.setLoadingAnimation()
                new_f = self.transform_image(file_path)
                self.setPixmap(QPixmap(new_f))

    def transform_image(self, file_path):
        if not os.path.exists("./outputs"):
            os.makedirs("./outputs")

        new_f = "./outputs/" + os.path.basename(file_path)
        transf.transform(file_path, new_f)
        return new_f

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.setAcceptDrops(True)

        self.isExtended = False

        # Main Layout: Adjust to custom schema (modify if necessary)
        mainLayout = QHBoxLayout()  # Using QHBoxLayout to organize elements horizontally
        self.setStyleSheet("background-color: #1e1616;")

        frame = QFrame(self)
        frame.setFrameShape(QFrame.Box)

        self.quickSettingsframe = QFrame(self)
        self.quickSettingsframe.setFrameShape(QFrame.Box)

        quickSettingsframeLayout = QVBoxLayout(self.quickSettingsframe)
        self.quickSettingsframe.setStyleSheet("background-color: #282020;border: 0px solid #ccc;")

        self.quickSettingsframe.hide()

        label1 = QLabel(self)
        label1.setText("Que souhaitez-vous obtenir ?")
        quickSettingsframeLayout.addWidget(label1)

        prompt1 = QTextEdit(self)
        quickSettingsframeLayout.addWidget(prompt1)
        prompt1.setStyleSheet('''
            QTextEdit {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        label2 = QLabel(self)
        label2.setText("Que souhaitez-vous éviter ?")
        quickSettingsframeLayout.addWidget(label2)

        prompt2 = QTextEdit(self)
        quickSettingsframeLayout.addWidget(prompt2)
        prompt2.setStyleSheet('''
            QTextEdit {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        label3 = QLabel(self)
        label3.setText("Intensité de modification de l'image")
        quickSettingsframeLayout.addWidget(label3)

        label4 = QFrame(self)
        label4.setFrameShape(QFrame.Box)
        label4Layout = QHBoxLayout(label4)
        label4.setStyleSheet("background-color: #282020;border: 0px solid #ccc;")

        label4a = QLabel(self)
        label4a.setText("Ne pas modifier")
        label4Layout.addWidget(label4a)

        label4b = QLabel(self)
        label4b.setText("Modifier totalement")
        label4Layout.addWidget(label4b)

        quickSettingsframeLayout.addWidget(label4)

        slider = QSlider(Qt.Horizontal, self)

        # Apply custom styles
        slider.setStyleSheet('''
            QSlider::groove:horizontal {
                height: 5px;
                background: #282020;
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }

            QSlider::handle:horizontal {
                background: #282020;
                border: 5px solid rgba(255, 0, 0, 0.5);
                width: 10px;
                height: 10px;
                margin-top: -10px;
                margin-bottom: -10px;
                cursor: pointer;
            }
        ''')


        slider.setRange(0, 100)  # Set range from 0 to 100
        slider.setValue(50)     # Set initial value to 50
        slider.setSingleStep(5) # Set single step size to 0.01
        quickSettingsframeLayout.addWidget(slider)

        label5 = QLabel(self)
        label5.setText("Quel style désirez-vous ?")
        quickSettingsframeLayout.addWidget(label5)

        self.combo1 = QComboBox()
        self.combo1.setStyleSheet('''
            QComboBox {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')
        quickSettingsframeLayout.addWidget(self.combo1)


        label6 = QLabel(self)
        label6.setText("Souhaitez-vous utiliser un sous-style ?")
        quickSettingsframeLayout.addWidget(label6)

        self.combo2 = QComboBox()
        quickSettingsframeLayout.addWidget(self.combo2)
        self.combo2.setStyleSheet('''
            QComboBox {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')
        self.combo2.addItem("Non")
        self.combo2.addItem("Non-")



        self.photoViewer = ImageLabel()
        frameLayout = QVBoxLayout(frame)
        frameLayout.addWidget(self.photoViewer)
        frame.setStyleSheet('border: 0px solid #ccc;')

        # Create a vertical button to place next to the photoViewer
        self.buttonExtend = QPushButton("ᐸ")
        self.buttonExtend.setStyleSheet('''
            QPushButton {
                background-color: #282020;
                color: red;
                padding: 10px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3e5f99;
            }
        ''')

        # Make the button fill the vertical space
        self.buttonExtend.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # Expanding vertically
        self.buttonExtend.clicked.connect(self.onExpandClicked)

        # Adding the frame and button into the main layout
        mainLayout.addWidget(self.quickSettingsframe)
        mainLayout.addWidget(self.buttonExtend)
        mainLayout.addWidget(frame)

        self.setLayout(mainLayout)

    def onExpandClicked(self):
        if self.isExtended:
            self.quickSettingsframe.hide()
            self.isExtended = False
            self.buttonExtend.setText("ᐸ")
        else:
            self.quickSettingsframe.show()
            self.isExtended = True
            self.buttonExtend.setText("ᐳ")

    def process_images_in_folder(self, folder_path):
        """Process all image files in the selected folder."""
        supported_formats = ('.png', '.xpm', '.jpg', '.jpeg', '.bmp')
        for file_name in os.listdir(folder_path):
            self.photoViewer.setLoadingAnimation()  # Set loading animation
            if file_name.lower().endswith(supported_formats):
                file_path = os.path.join(folder_path, file_name)
                new_f = self.photoViewer.transform_image(file_path)  # Process image
                self.photoViewer.setPixmap(QPixmap(new_f))  # Display processed image
                self.repaint()

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            event.accept()
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if os.path.isdir(file_path):
                    print(f"Dropped a folder: {file_path}")
                    self.process_images_in_folder(file_path)
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print(event)
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            self.set_image(file_path)
            event.accept()
        else:
            event.ignore()

    def set_image(self, file_path):
        self.photoViewer.setLoadingAnimation()
        new_f = self.photoViewer.transform_image(file_path)
        self.photoViewer.setPixmap(QPixmap(new_f))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = App()
    demo.show()
    sys.exit(app.exec_())
