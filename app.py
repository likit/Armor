import os
import wx
import pandas as pd
from components.gridtable import DataGrid, DataTable

VERSION = "0.1"


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent=parent, title=title)
        helpmenu = wx.Menu()
        filemenu = wx.Menu()
        gridmenu = wx.Menu()
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "About the program")
        menuImport = filemenu.Append(wx.ID_OPEN, "&Import", "Import data")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        menuCloseGrid = gridmenu.Append(wx.ID_CLOSE, "Close", "Close")
        menuSumGrid = gridmenu.Append(wx.ID_PREVIEW, "Summarize", "Summarize data")
        menuEditHeaderGrid = gridmenu.Append(wx.ID_EDIT, "Edit headers", "Edit headers")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(gridmenu, "&Grid")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnImport, menuImport)
        self.Bind(wx.EVT_MENU, self.OnCloseGrid, menuCloseGrid)
        self.Bind(wx.EVT_MENU, self.OnSumGrid, menuSumGrid)
        self.Bind(wx.EVT_MENU, self.OnEditHeaderGrid, menuEditHeaderGrid)

        self.CreateStatusBar(2)
        self.SetStatusText("Welcome to Armor!")

        self.Show(True)

    def OnAbout(self, e):
        aboutMsg = ('Armor Version %s\n\n'
                    'Developed at the Faculty of Medical Technology,\n'
                    'Mahidol University, Thailand,\n'
                    'to facilitate microbiology lab data analytics.\n\n'
                    'All right reserved (c) 2018\n\n'
                    'Please contact likit.pre@mahidol.edu for more information.' % VERSION)
        dlg = wx.MessageDialog(self, aboutMsg, "About Armour", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnImport(self, e):
        self.dirname = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            if filename.endswith('xlsx') or filename.endswith('xls'):
                self.df = pd.read_excel(os.path.join(dirname, filename))
            elif filename.endswith('csv'):
                self.df = pd.read_csv(os.path.join(dirname, filename))
        dlg.Destroy()
        self.SetStatusText('Data from file: {}'.format(os.path.join(dirname, filename)))
        self.SetStatusText('Total Row: {}, Column: {}'.format(len(self.df), len(self.df.columns)), 1)

        if not hasattr(self, 'dataPanel'):
            self.sizer = wx.BoxSizer(wx.VERTICAL)
            self.dataPanel = wx.Panel(self, -1)
            self.grid = DataGrid(self.dataPanel, data=self.df)
            self.sizer.Add(self.grid, 1, wx.EXPAND | wx.ALL)
            self.dataPanel.SetSizer(self.sizer)
            self.sizer.Fit(self.dataPanel)
            # self.Layout()  # Layout does not work like we would expect
        else:
            self.dataPanel.Hide()
            self.grid.SetTable(DataTable(self.df))  # update data model
            self.dataPanel.Show()
        self.Fit()  # Fit seems to suffice in this case

    def OnExit(self, e):
        self.Close(True)

    def OnCloseGrid(self, e):
        if hasattr(self, 'dataPanel'):
            if self.dataPanel.IsShown():
                self.dataPanel.Hide()
                self.Layout()

    def OnSumGrid(self, e):
        childFrame = wx.Frame(self, title="Description")
        self.desgrid = DataGrid(childFrame, data=self.df.describe())
        childFrame.Show()

    def OnEditHeaderGrid(self, e):
        dlg = wx.Frame(self, title='Edit Headers')
        hdrList = wx.ListCtrl(dlg, -1, style=wx.LC_REPORT)
        dtypes = self.df.dtypes
        for col, text in enumerate(['no.', 'headers', 'mappers', 'dtype', 'drug', 'show']):
            hdrList.InsertColumn(col, text)

        for idx, header in enumerate(self.df.columns):
            index = hdrList.InsertStringItem(idx, str(idx+1))
            hdrList.SetStringItem(index, 1, header)
            hdrList.SetStringItem(index, 3, str(dtypes[header]))


        # okButton = wx.Button(dlg, wx.ID_OK, "Ok", pos=(15,15))
        # okButton.SetDefault()
        # cancelButton = wx.Button(dlg, wx.ID_CANCEL, "Cancel", pos=(115, 15))
        dlg.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, "Armor v.%s" % VERSION)
    app.MainLoop()
