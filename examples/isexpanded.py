import sys
from PyQt5 import QtCore, QtGui, QtWidgets

dataSets = [
    {
        "itemA" :{
            "menuA": ["a101", "a102"],
        },
        "itemBC": {
            "menuC": ["c101", "c102", "c103"],
            "menuB": ["b101"]
        },
    }, 
    {
        "itemD" :{
            "menuD": ["d100"],
        },
    }

]

class TreeModel(QtGui.QStandardItemModel):
    checkStateChange = QtCore.pyqtSignal(QtCore.QModelIndex, bool)
    def __init__(self, dataSet):
        super(TreeModel, self).__init__()

        # unserialize data, as per your original code; you might want to use a
        # recursive function instead, to allow multiple levels of items
        for page_name, page_contents in dataSet.items():
            for pk, pv in page_contents.items():
                parent = QtGui.QStandardItem(pk)
                parent.setCheckable(True)
                self.appendRow(parent)
                if pv:
                    parent.setTristate(True)
                    for c in pv:
                        child = QtGui.QStandardItem(c)
                        child.setCheckable(True)
                        parent.appendRow(child)

        self.dataChanged.connect(self.checkStateChange)

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.CheckStateRole:
            childState = QtCore.Qt.Checked if value else QtCore.Qt.Unchecked
            # set all children states according to this parent item
            for row in range(self.rowCount(index)):
                for col in range(self.columnCount(index)):
                    childIndex = self.index(row, col, index)
                    self.setData(childIndex, childState, QtCore.Qt.CheckStateRole)
            # if the item has a parent, emit the dataChanged signal to ensure
            # that the parent state is painted correctly according to what data()
            # will return; note that this will emit the dataChanged signal whatever
            # the "new" parent state is, meaning that it might still be the same
            parent = self.parent(index)
            if parent.isValid():
                self.dataChanged.emit(parent, parent)
        return super(TreeModel, self).setData(index, value, role)

    def data(self, index, role=QtCore.Qt.DisplayRole):
        # QStandardItemModel doesn't support auto tristate based on its children 
        # as it does for QTreeWidget's internal model; we have to implement that
        if role == QtCore.Qt.CheckStateRole and self.flags(index) & QtCore.Qt.ItemIsTristate:
            childStates = []
            # collect all child check states
            for row in range(self.rowCount(index)):
                for col in range(self.columnCount(index)):
                    childIndex = self.index(row, col, index)
                    childState = self.data(childIndex, QtCore.Qt.CheckStateRole)
                    # if the state of a children is partially checked we can
                    # stop here and return a partially checked state
                    if childState == QtCore.Qt.PartiallyChecked:
                        return QtCore.Qt.PartiallyChecked
                    childStates.append(childState)
            if all(childStates):
                # all children are checked, yay!
                return QtCore.Qt.Checked
            elif any(childStates):
                # only some children are checked...
                return QtCore.Qt.PartiallyChecked
            # no item is checked, so bad :-(
            return QtCore.Qt.Unchecked
        return super(TreeModel, self).data(index, role)

    def checkStateChange(self, topLeft, bottomRight):
        # if you need some control back to your data outside the model, here is
        # the right place to do it; note that *usually* the topLeft and 
        # bottomRight indexes are the same, expecially with QStandardItemModels
        # but that would not be the same in some special cases
        pass


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.treeView = QtWidgets.QTreeView()
        layout.addWidget(self.treeView)

        self.models = []
        self.expandStates = {}

        for i, dataSet in enumerate(dataSets):
            model = TreeModel(dataSet)
            button = QtWidgets.QPushButton('Data-{:02}'.format(i + 1))
            layout.addWidget(button)
            button.clicked.connect(lambda _, model=model: self.setModel(model))

    def getExpandState(self, expDict, model, index=QtCore.QModelIndex()):
        # set the index expanded state, if it's not the root index:
        # the root index is not a valid index!
        if index.isValid():
            expDict[index] = self.treeView.isExpanded(index)
        # if the index (or root index) has children, set their states
        for row in range(model.rowCount(index)):
            for col in range(model.columnCount(index)):

                childIndex = model.index(row, col, index)
                # if the current index has children, set their expand state
                # using this function, which is recursive
                for childRow in range(model.rowCount(childIndex)):
                    self.getExpandState(expDict, model, childIndex)

    def setModel(self, model):
        if self.treeView.model():
            if self.treeView.model() == model:
                # the model is the same, no need to update anything
                return
            # save the expand states of the current model before changing it
            prevModel = self.treeView.model()
            self.expandStates[prevModel] = expDict = {}
            self.getExpandState(expDict, prevModel)
        self.treeView.setModel(model)
        
        if model in self.expandStates:
            # if the new model has expand states saved, restore them
            for index, expanded in self.expandStates.get(model, {}).items():
                self.treeView.setExpanded(index, expanded)
        else:
            self.treeView.expandAll()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Window()
    w.show()
    sys.exit(app.exec_())