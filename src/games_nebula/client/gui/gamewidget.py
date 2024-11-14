import os
import urllib.request
from games_nebula.client.translator import _tr
from games_nebula.client.gui.vboxlayout import VBoxLayout
from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import Qt, QObject, QRunnable, QThreadPool, pyqtSignal
    from PyQt6.QtGui import QImage, QPixmap
    from PyQt6.QtWidgets import QPushButton, QWidget, QLabel
elif __qt_version__ == '5':
    from PyQt5.QtCore import Qt, QObject, QRunnable, QThreadPool, pyqtSignal
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtWidgets import QPushButton, QWidget, QLabel

class GameWidget(QWidget):
    def __init__(self, slug, title, logo_path, logo_url, installed):
        super(GameWidget, self).__init__()
        self.slug = slug
        self.title = title
        self.logo_path = logo_path
        self.logo_url = logo_url
        self.installed = installed
        self.__image = QLabel()
        self.__qimage = QImage()
        self.__image.setToolTip(title)
        self.button = QPushButton(_tr("Install"))
        if installed:
            self.button.setText(_tr("Play"))
        layout = VBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10) # 10 is default
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidgets(self.__image, self.button)
        self.setLayout(layout)

    def set_logo(self):
        self.__qimage.load(self.logo_path)
        if not self.installed:
            self.__qimage = self.__qimage.convertToFormat(QImage.Format.Format_Grayscale8)
        #self.__image.setPixmap(QPixmap(self.__qimage).scaledToWidth(self.logo_width))
        self.__image.setPixmap(QPixmap(self.__qimage))

    def scale_logo(self, width):
        if not self.__qimage.isNull():
            self.__image.setPixmap(QPixmap(self.__qimage.scaledToWidth(width)))

    def download_logo(self):
        resp = urllib.request.urlopen(self.logo_url)
        data = resp.read()
        logo_dir = os.path.dirname(self.logo_path)
        if not os.path.exists(logo_dir): os.makedirs(logo_dir)
        with open(self.logo_path, 'wb') as f:
            f.write(data)
