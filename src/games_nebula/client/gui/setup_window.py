import os
import time
from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import (
            QObject, QRunnable, QThreadPool, pyqtSignal
    )
    from PyQt6.QtGui import (
            QImage, QPixmap, QIcon
    )
    from PyQt6.QtWidgets import (
            QDialog, QHBoxLayout, QLabel
    )
elif __qt_version__ == '5':
    from PyQt5.QtCore import (
            QObject, QRunnable, QThreadPool, pyqtSignal
    )
    from PyQt5.QtGui import (
            QImage, QPixmap, QIcon
    )
    from PyQt5.QtWidgets import (
            QDialog, QHBoxLayout, QLabel
    )
from games_nebula.client.translator import _tr
from games_nebula.client.gui.main_window import MainWindow

class SetupWindow(QDialog):
    class __SetupRunnable(QRunnable):
        class __RunnableSignals(QObject):
            finished = pyqtSignal()
        singnals = __RunnableSignals()

        def __init__(self):
            QRunnable.__init__(self)
            pass

        def run(self):
            #TODO Update db here
            time.sleep(1) # give the window a chance to appear :)
            self.singnals.finished.emit()

    def __init__(self):
        super(SetupWindow, self).__init__()
        if os.path.exists('../data/icons/games_nebula.png'):
            data_path = '../data'
        else:
            data_path = '/usr/share'
        self.setWindowIcon(QIcon(f'{data_path}/icons/games_nebula.png'))
        self.setWindowTitle("Games Nebula")
        image = QLabel()
        qimage = QImage()
        qimage.load(f'{data_path}/icons/games_nebula.png')
        image.setPixmap(QPixmap(qimage).scaledToWidth(32))
        label = QLabel(_tr("Launching..."))
        layout = QHBoxLayout()
        layout.addWidget(image)
        layout.addWidget(label)
        self.setLayout(layout)

    def setup(self):
        def __show_main_window():
            mainWin = MainWindow()
            mainWin.show()
            self.hide()
        runnable = self.__SetupRunnable()
        runnable.singnals.finished.connect(__show_main_window)
        thread_pool = QThreadPool.globalInstance()
        thread_pool.start(runnable)
