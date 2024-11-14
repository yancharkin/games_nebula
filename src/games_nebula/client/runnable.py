from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtCore import QObject, QRunnable, pyqtSignal
elif __qt_version__ == '5':
    from PyQt5.QtCore import QObject, QRunnable, pyqtSignal

class Runnable(QRunnable):
    class __RunnableSignals(QObject):
        finished = pyqtSignal(tuple)
    singnals = __RunnableSignals()

    def __init__(self, func_to_run, *func_args):
        QRunnable.__init__(self)
        self.func_to_run = func_to_run
        self.func_args = func_args

    def run(self):
        self.func_to_run(*self.func_args)
        self.singnals.finished.emit(self.func_args)
