import wx
import wx.grid

class DataTable(wx.grid.PyGridTableBase):
    def __init__(self, data):
        wx.grid.PyGridTableBase.__init__(self)
        if not data.empty:
            self.data = data

    def GetNumberRows(self):
        return len(self.data)

    def GetNumberCols(self):
        return len(self.data.columns)

    def GetColLabelValue(self, col):
        return self.data.columns[col]

    def GetRowLabelValue(self, row):
        return self.data.index[row]

    def IsEmptyCell(self, row, col):
        return False

    def GetValue(self, row, col):
        return self.data.iloc[row, col]

    def SetValue(self, row, col, value):
        pass

class DataGrid(wx.grid.Grid):
    def __init__(self, parent, data=None):
        wx.grid.Grid.__init__(self, parent, -1)
        self.SetTable(DataTable(data))
