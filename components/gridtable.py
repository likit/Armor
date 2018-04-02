import wx
import wx.grid

class DataTable(wx.grid.PyGridTableBase):
    data = (("CF", "Bob", "Dernier"), ("2B", "Ryne", "Sandberg"))
    colLabels = ("Last", "First")

    def __init__(self):
        wx.grid.PyGridTableBase.__init__(self)

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data[0]) - 1

    def GetColLabelValue(self, col):
        return self.colLabels[col]

    def GetRowLabelValue(self, row):
        return self.data[row][0]

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data[row][col + 1]

    def SetValue(self, row, col, value):
        pass

class DataGrid(wx.grid.Grid):
    def __init__(self, parent):
        wx.grid.Grid.__init__(self, parent, -1)
        self.SetTable(DataTable())
