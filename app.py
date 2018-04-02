import os
import wx
from components.gridtable import DataGrid

VERSION = "0.1"

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent=parent, title=title)
        helpmenu = wx.Menu()
        filemenu = wx.Menu()
        gridmenu = wx.Menu()
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "About the program")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open a file")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        menuCloseGrid = gridmenu.Append(wx.ID_CLOSE, "Close", "Close")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(gridmenu, "&Grid")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        self.Bind(wx.EVT_MENU, self.OnCloseGrid, menuCloseGrid)

        self.panel = wx.Panel(self, -1)
        self.Show(True)


    def OnAbout(self, e):
        aboutMsg = ('Armour Version %s\n\n'
                    'Developed at the Faculty of Medical Technology,\n'
                    'Mahidol University, Thailand,\n'
                    'to facilitate microbiology lab data analytics.\n\n'
                    'All right reserved (c) 2018\n\n'
                    'Please contact likit.pre@mahidol.edu for more information.' % VERSION)
        dlg = wx.MessageDialog(self, aboutMsg, "About Armour", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnOpen(self, e):
        self.dirname = ''
        dlg = wx.FileDialog(self, 'Choose a file', self.dirname, '', '*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
            f = open(os.path.join(self.dirname, self.filename), 'r')
            f.close()
        dlg.Destroy()
        if self.panel.IsShown():
            self.panel.Destroy()
            # self.Layout()
            self.Fit()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.dataPanel = wx.Panel(self, -1)
        self.grid = DataGrid(self.dataPanel)
        self.sizer.Add(self.grid, 1, wx.EXPAND|wx.ALL)
        self.dataPanel.SetSizer(self.sizer)
        self.sizer.Fit(self.dataPanel)
        # self.Layout()  # Layout does not work like we would expect
        self.Fit()       # Fit seems to suffice in this case

    def OnExit(self, e):
        self.Close(True)

    def OnCloseGrid(self, e):
        if self.dataPanel.IsShown():
            self.dataPanel.Destroy()
            self.Layout()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, "Armor v.%s" % VERSION)
    app.MainLoop()
