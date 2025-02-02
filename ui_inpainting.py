import sys
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QDialog
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint, QPointF
from diffusers import StableDiffusionXLInpaintPipeline
from PIL import Image, ImageDraw

class InpaintingApp(QDialog):
    def __init__(self, file_name):
        super().__init__()

        self.setWindowTitle("Dessinez la zone à modifier")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(self.size())

        self.layout = QVBoxLayout()

        self.setStyleSheet("background-color: #1e1616;")

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.inpaint_button = QPushButton("Valider", self)
        self.inpaint_button.clicked.connect(self.run_inpainting)
        self.inpaint_button.setStyleSheet('''
            QPushButton {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        self.layout.addWidget(self.inpaint_button)
        self.setLayout(self.layout)

        self.original_image = None
        self.mask_image = None
        self.display_pixmap = None
        self.scale_factor = 1.0
        self.image_offset = QPoint(0, 0)

        self.drawing = False
        self.last_point = QPoint()

        self.load_image(file_name)

    def run_inpainting(self):
        if self.original_image is not None and self.mask_image is not None:
            self.close()

    def pil_to_qimage(self, image):
        image = image.convert("RGB")
        data = image.tobytes("raw", "RGB")
        return QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)

    def load_image(self, image_path):
        if image_path:
            self.original_image = Image.open(image_path).convert("RGB")
            self.mask_image = Image.new("L", self.original_image.size, 0)
            self.show_image(self.original_image)

    def show_image(self, image):
        q_image = self.pil_to_qimage(image)
        pixmap = QPixmap.fromImage(q_image)

        self.display_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(self.display_pixmap)
        self.image_offset = QPoint((self.image_label.width() - self.display_pixmap.width()) // 2,
                                   (self.image_label.height() - self.display_pixmap.height()) // 2)
        self.scale_factor = min(self.image_label.width() / pixmap.width(),
                                self.image_label.height() / pixmap.height())

    def resizeEvent(self, event):
        if self.original_image is not None:
            self.show_image(self.original_image)
        super().resizeEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.display_pixmap:
            self.drawing = True
            self.last_point = self.get_image_coordinates(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing and self.display_pixmap:
            current_point = self.get_image_coordinates(event.pos())

            painter = QPainter(self.display_pixmap)
            painter.setPen(QPen(Qt.red, 10, Qt.SolidLine))

            radius = 10
            painter.drawEllipse(current_point - self.image_offset,  radius, radius)
            painter.end()
            self.image_label.setPixmap(self.display_pixmap)

            draw = ImageDraw.Draw(self.mask_image)
            x = (current_point.x() - self.image_offset.x()) / self.scale_factor
            y = (current_point.y() - self.image_offset.y()) / self.scale_factor


            radius = 20*2
            draw.ellipse([
                x - radius / 2, y - radius / 2,
                x + radius / 2, y + radius / 2
            ], fill=255)

            self.last_point = current_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def get_image_coordinates(self, pos):
        return pos

if __name__ == "__main__":
    app = QApplication(sys.argv)
    file_name = QFileDialog.getOpenFileName(None, "Select Image", "", "Images (*.png *.jpg *.bmp)")[0]
    if file_name:
        main_window = InpaintingApp(file_name)
        main_window.show()
        sys.exit(app.exec_())
