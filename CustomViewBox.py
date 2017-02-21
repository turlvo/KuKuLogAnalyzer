import pyqtgraph as pg
from  PyQt4.QtCore import *

class CustomViewBox(pg.ViewBox):
    def __init__(self, *args, **kwds):
        pg.ViewBox.__init__(self, *args, **kwds)
        self.setMouseMode(self.RectMode)

    ## reimplement right-click to zoom out
    def mouseClickEvent(self, ev):
        if ev.button() == Qt.RightButton:
            self.autoRange()

    # def mouseDragEvent(self, ev):
    #     if ev.button() == Qt.RightButton:
    #         ev.ignore()
    #     else:
    #         pg.ViewBox.mouseDragEvent(self, ev)