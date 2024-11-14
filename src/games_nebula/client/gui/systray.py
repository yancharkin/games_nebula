import os
from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
    from PyQt6.QtGui import QIcon
elif __qt_version__ == '5':
    from PyQt5.QtWidgets import QSystemTrayIcon, QMenu
    from PyQt5.QtGui import QIcon
from games_nebula.client.gui.main_window import MainWindow
from games_nebula.client.translator import _tr

class Systray:
    """Tray icon."""

    def __init__(self, parent):
        self.parent = parent
        if os.path.exists('../data/icons/games_nebula.png'):
            icon = QIcon('../data/icons/games_nebula.png')
        else:
            icon = QIcon('/usr/share/icons/games_nebula.png')
        self.tray = QSystemTrayIcon(QIcon(icon), self.parent)
        self.tray.activated.connect(self.cb_clicked)
        context_menu = QMenu()
        action_settings = context_menu.addAction(_tr("Settings"))
        #action_settings.triggered.connect(self.cb_action_settings)
        action_exit = context_menu.addAction(_tr("Exit"))
        action_exit.triggered.connect(self.cb_action_exit)
        self.tray.setContextMenu(context_menu)

    def show(self):
        self.tray.show()

    def cb_clicked(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            for widget in self.parent.topLevelWidgets():
                if isinstance(widget, MainWindow):
                    if widget.isVisible():
                        widget.hide()
                    else:
                        widget.show()

    def cb_action_exit(self):
        self.parent.quit()

