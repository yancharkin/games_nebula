__version__ = '2024.dev1'
__qt_version__ = '6'

if __qt_version__ == '6':
    try:
        from PyQt6.QtCore import qVersion
        __qt_version__ = qVersion()
    except:
        from PyQt5.QtCore import qVersion
        __qt_version__ = qVersion()

__qt_version__ = __qt_version__.split('.')[0]
