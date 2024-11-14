#!/usr/bin/env python3
# -*- coding: utf-8; -*-

################################################################################
## Based on PyQt5 example:
## https://github.com/baoboa/pyqt5/blob/master/examples/layouts/flowlayout.py
################################################################################

from games_nebula import __qt_version__
if __qt_version__ == '6':
    from PyQt6.QtWidgets import QLayout, QSizePolicy
    from PyQt6.QtCore import QSize, QRect, Qt, QPoint
if __qt_version__ == '5':
    from PyQt5.QtWidgets import QLayout, QSizePolicy
    from PyQt5.QtCore import QSize, QRect, Qt, QPoint

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=0, verticalSpacing=0):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.verticalSpacing = verticalSpacing
        self.itemList = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            wid = item.widget()
            spaceX = wid.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Horizontal
            )
            spaceY = wid.style().layoutSpacing(
                    QSizePolicy.ControlType.PushButton,
                    QSizePolicy.ControlType.PushButton,
                    Qt.Orientation.Vertical
            )
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY + self.verticalSpacing
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            item_width = item.widget().geometry().width()
            items_n = rect.width() // item_width
            try:
                horizontalSpacing = (rect.width() - items_n * item_width) // (items_n + 1)
            except:
                horizontalSpacing = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x+horizontalSpacing, y+self.verticalSpacing), item.sizeHint()))

            x = nextX + horizontalSpacing
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()
