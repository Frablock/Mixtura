import sys, os, signal
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog, QHBoxLayout, QFrame, QPushButton, QSizePolicy, QTextEdit, QSlider, QComboBox, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie, QImage

from PIL import Image

import transf
import model_finder as mf
import ui_inpainting as inp
import more_windows as mw

signal.signal(signal.SIGINT, signal.SIG_DFL)

LOADING_IMAGE = os.path.join(os.path.dirname(__file__), "reload-cat.gif")
signal.signal(signal.SIGINT, signal.SIG_DFL) # Support du CTRL+C
BASE_IMAGE = None
MASK_IMAGE = None

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
        self.movie = None  # Maintient anim chargement
        self.pixmap_image = None
        self.fi_size = self.size()
        print("c",self.size())

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
        self.pixmap_image = image

        scaled_pixmap = image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled_pixmap)
        self.fi_size = self.size()

    def updatePixmap(self):
        # Redimention des images en conservant le ratio
        scaled_pixmap = self.pixmap_image.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        super().setPixmap(scaled_pixmap)
        self.fi_size = self.size()

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

        global BASE_IMAGE
        BASE_IMAGE = file_path

        theApp.original_window.setPixmap(QPixmap(BASE_IMAGE))
        theApp.original_window.show()
        theApp.repaint()

        theApp.buttonInpainting.show()
        theApp.buttonRedo.show()

        new_f = "./outputs/" + os.path.basename(file_path)
        if theApp.inpaint_window != None:
            if theApp.inpaint_window.CheckUse.isChecked():
                transf.inpaint(file_path, new_f, MASK_IMAGE, prompt1.toPlainText(), prompt2.toPlainText(), slider.value()/100, model=theApp.combo1.currentText())
                return new_f
        transf.transform(file_path, new_f, prompt1.toPlainText(), prompt2.toPlainText(), slider.value()/100, model=theApp.combo1.currentText())
        return new_f

class App(QWidget):
    def __init__(self):
        global prompt1, prompt2, slider, width, height
        super().__init__()

        screen = QApplication.primaryScreen()
        screen_size = screen.availableGeometry()

        width = screen_size.width()
        height = screen_size.height()
        # self.resize(width, height) # fullscreen
        self.resize(800,600)
        #self.setFixedSize(self.size()) # blockage plein écran

        self.setWindowTitle("Mixtura")
        self.setAcceptDrops(True)

        self.isExtended = False

        mainLayout = QHBoxLayout()
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


        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setSingleStep(5)
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
        for ele in mf.getAllModelsNameAndTag():
            self.combo1.addItem(ele)

        self.combo1.currentTextChanged.connect(self.on_combobox1_changed)


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

        self.buttonRedo = QPushButton("Traiter l'image")
        self.buttonRedo.clicked.connect(self.onRedoClicked)
        self.buttonRedo.setStyleSheet('''
            QPushButton {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')



        self.photoViewer = ImageLabel()
        frameLayout = QVBoxLayout(frame)
        frameLayout.addWidget(self.photoViewer)
        frame.setStyleSheet('border: 0px solid #ccc;')

        # Le bouton vertical permettant d'afficher/cacher le menu
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

        # On étends le bouton
        self.buttonExtend.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # Expension verticale
        self.buttonExtend.clicked.connect(self.onExpandClicked)

        self.buttonLayout = QHBoxLayout()

        self.buttonInpainting = QPushButton("Éditer une zone")
        self.buttonInpainting.setStyleSheet('''
            QPushButton {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        self.buttonInpainting.hide()
        self.buttonRedo.hide()
        self.buttonInpainting.clicked.connect(self.onInpaintClicked)

        self.buttonLayout.addWidget(self.buttonRedo)
        self.buttonLayout.addWidget(self.buttonInpainting)

        frameLayout.addLayout(self.buttonLayout)

        self.original_window = mw.OriginalWindow()
        self.original_window.hide()

        self.inpaint_window = None

        mainLayout.addWidget(self.quickSettingsframe)
        mainLayout.addWidget(self.buttonExtend)
        mainLayout.addWidget(frame)

        self.setLayout(mainLayout)
    def onInpaintClicked(self):
        global MASK_IMAGE
        inpaintingWindow = inp.InpaintingApp(BASE_IMAGE)
        inpaintingWindow.exec_()

        MASK_IMAGE = inpaintingWindow.mask_image
        self.inpaint_window = mw.InpaintWindow()
        self.inpaint_window.show()

        self.inpaint_window.labelInpaint.setPixmap(inpaintingWindow.display_pixmap)
        self.inpaint_window.CheckUse.setChecked(True)

    def onExpandClicked(self):
        if self.isExtended:
            self.quickSettingsframe.hide()
            self.isExtended = False
            self.buttonExtend.setText("ᐸ")
        else:
            self.quickSettingsframe.show()
            self.isExtended = True
            self.buttonExtend.setText("ᐳ")

    def onRedoClicked(self):
        if BASE_IMAGE != None:
            self.set_image(BASE_IMAGE)

    def on_combobox1_changed(self, value):
        transf.change_pipeline(mf.models[mf.getAllModelsNameAndTag()[value]])

    def process_images_in_folder(self, folder_path):
        supported_formats = ('.png', '.xpm', '.jpg', '.jpeg', '.bmp')
        for file_name in os.listdir(folder_path):
            self.photoViewer.setLoadingAnimation()
            if file_name.lower().endswith(supported_formats):
                file_path = os.path.join(folder_path, file_name)
                new_f = self.photoViewer.transform_image(file_path)
                self.photoViewer.setPixmap(QPixmap(new_f))
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
    theApp = App()
    theApp.show()
    sys.exit(app.exec_())
