from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtWidgets import QVBoxLayout
elif __qt_version__ == '5':
    from PyQt5.QtWidgets import QVBoxLayout

class VBoxLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super(VBoxLayout, self).__init__(parent)

    def addWidgets(self, *widgets):
        for widget in widgets:
            self.addWidget(widget)
