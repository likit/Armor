import os
import wx

VERSION = "0.1"

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent=parent, title=title)
        helpmenu = wx.Menu()
        filemenu = wx.Menu()
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "About the program")
        menuOpen = filemenu.Append(wx.ID_OPEN, "&Open", "Open a file")
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)

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
            print(f.readline())
            f.close()
        dlg.Destroy()

    def OnExit(self, e):
        self.Close(True)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, "Armour %s" % VERSION)
    app.MainLoop()
