from PyQt4.QtCore import *

class TableModel(QAbstractTableModel):
    """
    keep the method names
    they are an integral part of the model
    """
    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        if len(self.mylist) > 0:
            return len(self.mylist[0])
        else:
            return 0

    def update(self, dataIn):
        self.emit(SIGNAL("LayoutAboutToBeChanged()"))
        self.arraydata = datain
        self.emit(SIGNAL("LayoutChanged()"))
        self.dataChanged.emit(self.createIndex(0, 0),
                              self.createIndex(self.rowCount(0),
                                               self.columnCount(0)))
        self.emit(SIGNAL("DataChanged(QModelIndex,QModelIndex)"),
                  self.createIndex(0, 0),
                  self.createIndex(self.rowCount(0),
                                   self.columnCount(0)))

    def setData(self, data):
        self.mylist = data
        return True

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]


    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))