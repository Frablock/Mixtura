import sys
import torch
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget, QLineEdit
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
from diffusers import StableDiffusionXLInpaintPipeline
from PIL import Image, ImageDraw
import numpy as np

# Load the SDXL Inpainting Pipeline from HuggingFace
device = "cuda" if torch.cuda.is_available() else "cpu"
pipe = StableDiffusionXLInpaintPipeline.from_single_file(
    #"/home/user/Documents/Stable Diffusion/stable-diffusion-webui/models/Stable-diffusion/ponyRealism_v21MainVAE.safetensors",
    "/home/user/Documents/Stable Diffusion/stable-diffusion-webui/models/Stable-diffusion/albedobaseXL_v21.safetensors",
    torch_dtype=torch.float16
)
pipe = pipe.to(device)

class InpaintingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SDXL Inpainting with PyQt")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(self.size())

        # Create main widget and layout
        self.central_widget = QWidget(self)
        self.layout = QVBoxLayout(self.central_widget)

        # QLabel to show the image
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.image_label)

        # Button to load image
        self.load_button = QPushButton("Load Image", self)
        self.load_button.clicked.connect(self.load_image)
        self.layout.addWidget(self.load_button)

        # Button to run inpainting
        self.inpaint_button = QPushButton("Run Inpainting", self)
        self.inpaint_button.clicked.connect(self.run_inpainting)
        self.layout.addWidget(self.inpaint_button)
        self.prompt1 = QLineEdit(self)
        self.layout.addWidget(self.prompt1)
        self.prompt1.setStyleSheet('''
            QLineEdit {
                border: 2px solid rgba(255, 0, 0, 0.5);
                border-radius: 5px;
            }
        ''')

        self.setCentralWidget(self.central_widget)

        # Variables to hold the image and mask
        self.original_image = None
        self.mask_image = None
        self.display_pixmap = None
        self.scale_factor = 1.0
        self.image_offset = QPoint(0, 0)

        # Graphics for drawing mask
        self.drawing = False
        self.last_point = QPoint()

    def load_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.xpm *.jpg *.jpeg)")

        if image_path:
            self.original_image = Image.open(image_path).convert("RGB")
            self.mask_image = Image.new("L", self.original_image.size, 0)
            self.show_image(self.original_image)

    def show_image(self, image):
        q_image = self.pil_to_qimage(image)
        pixmap = QPixmap.fromImage(q_image)

        # Scale the image to fit the label while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

        # Calculate scale factor and offset
        self.scale_factor = min(self.image_label.width() / pixmap.width(),
                                self.image_label.height() / pixmap.height())

        self.image_offset = QPoint((self.image_label.width() - scaled_pixmap.width()) // 2,
                                   (self.image_label.height() - scaled_pixmap.height()) // 2)

        self.display_pixmap = scaled_pixmap

    def pil_to_qimage(self, image):
        image = image.convert("RGB")
        data = image.tobytes("raw", "RGB")
        return QImage(data, image.size[0], image.size[1], QImage.Format_RGB888)

    def run_inpainting(self):
        if self.original_image is not None and self.mask_image is not None:
            self.mask_image.show()
            # Run the pipeline
            image = pipe(
                prompt=self.prompt1.text()+", highly detailed, high contrast",
                negative_prompt="deformed, deformed face, low quality, bad quality, worst quality, (drawn, furry, illustration, cartoon,  comic:1.5), 3d, cgi, extra fingers, (source_cartoon, source_furry, source_western, source_comic, source_pony), deformed teeth, porn, nsfw, nude, suggestive, score_3, score_2, score_1, bad quality",
                image=self.original_image,
                mask_image=self.mask_image,
                guidance_scale=7,
                strength=0.75,
                num_inference_steps=50,
            ).images[0]

            self.show_image(image)
            self.mask_image = Image.new("L", self.original_image.size, 0)
            self.original_image = image


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.display_pixmap:
            self.drawing = True
            self.last_point = self.get_image_coordinates(event.pos())

    def mouseMoveEvent(self, event):
        if self.drawing and self.display_pixmap:
            current_point = self.get_image_coordinates(event.pos())

            # Draw on display pixmap
            painter = QPainter(self.display_pixmap)
            painter.setPen(QPen(Qt.red, 10, Qt.SolidLine))

            # Draw a circle instead of a line
            radius = 10  # Radius of the circle
            painter.drawEllipse(current_point - self.image_offset, radius, radius)
            painter.end()
            self.image_label.setPixmap(self.display_pixmap)

            # Draw on mask
            draw = ImageDraw.Draw(self.mask_image)
            x = (current_point.x() - self.image_offset.x()) / self.scale_factor
            y = (current_point.y() - self.image_offset.y()) / self.scale_factor

            # Draw a circle on the mask (ellipse with equal width and height for a circle)
            radius = 40*2  # Diameter of the circle
            draw.ellipse([
                x - radius / 2, y - radius / 2,
                x + radius / 2, y + radius / 2
            ], fill=255)

            self.last_point = current_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def get_image_coordinates(self, pos):
        return pos - self.image_label.pos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = InpaintingApp()
    main_window.show()
    sys.exit(app.exec_())
