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
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Exit the program")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "About the program")
        menuImport = gridmenu.Append(wx.ID_OPEN, "&Import", "Import data to grid")
        menuSumGrid = gridmenu.Append(wx.ID_PREVIEW, "Summarize", "Summarize data")
        menuEditHeaderGrid = gridmenu.Append(wx.ID_EDIT, "Edit headers", "Edit headers")
        menuCloseGrid = gridmenu.Append(wx.ID_CLOSE, "Close", "Close the opened grid")

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

        # a schema file
        self.schemafilename = ''
        self.schemadirname = ''

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
        dlg = wx.FileDialog(self, 'Choose a file', defaultDir=os.getcwd(),
                                defaultFile="", wildcard='*.xls;*.xlsx;*.csv', style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            filename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            if filename.endswith('xlsx') or filename.endswith('xls'):
                self.df = pd.read_excel(os.path.join(dirname, filename))
            elif filename.endswith('csv'):
                self.df = pd.read_csv(os.path.join(dirname, filename))
        else:
            dirname = None
            filename = None
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

        columns = ['no.', 'header', 'mapper', 'dtype', 'drug', 'show']
        headdf = pd.DataFrame(columns=columns)

        def createNewHeaderSchemaList(theList, dataframe, columns):
            headerdata = []
            dtypes = dataframe.dtypes
            for col, text in enumerate(columns):
                theList.InsertColumn(col, text)

            for idx, header in enumerate(dataframe.columns):
                index = theList.InsertStringItem(idx, str(idx+1))
                theList.SetStringItem(index, 1, header)
                theList.SetStringItem(index, 2, header)
                theList.SetStringItem(index, 3, str(dtypes[header]))
                headerdata.append({
                    'no.': str(idx+1),
                    'header': header,
                    'dtype': str(dtypes[header]),
                    'mapper': header
                })

            theList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(3, wx.LIST_AUTOSIZE)
            return headerdata

        def createHeaderSchemaListFromFile(theList, dataframe, columns):
            theList.ClearAll()
            for col, text in enumerate(columns):
                theList.InsertColumn(col, text)

            for idx, row in enumerate(dataframe.iterrows()):
                item = row[1]
                index = theList.InsertStringItem(idx, str(idx+1))
                for n, colname in enumerate(columns[1:]):
                    theList.SetStringItem(index, n+1, str(item[colname]))

            theList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(3, wx.LIST_AUTOSIZE)


        def OnImport(event, theList, dataframe, columns):
            openDlg = wx.FileDialog(self, 'Choose a file', self.schemadirname, '', '*.csv;', wx.FD_OPEN)
            if openDlg.ShowModal() == wx.ID_OK:
                self.schemafilename = openDlg.GetFilename()
                self.schemadirname = openDlg.GetDirectory()
                try:
                    dataframe = pd.read_csv(
                        os.path.join(self.schemadirname, self.schemafilename))
                    print(dataframe.head())
                except:
                    alertdialog = wx.MessageDialog(self,
                        'An error occurred. Cannot load a schema from the file.')
                    alertdialog.ShowModal()
                else:
                    try:
                        createHeaderSchemaListFromFile(theList, dataframe, columns)
                    except Exception as e:
                        alertdialog = wx.MessageDialog(self,
                                           'An error occurred. Cannot display a schema.')
                        alertdialog.ShowModal()
                        raise e

        def OnSave(event, data):
            if not self.filename:  # the schema has never been saved before
                OnSaveAs(event, data)
            else:
                try:
                    data.to_csv(os.path.join(self.dirname, self.filename), index=False)
                except:
                    alertdialog = wx.MessageDialog(self, 'An error occurred. Cannot save a scheme to disk.')

        def OnClose(event):
            dlg.Hide()

        def OnSaveAs(event, data):
            saveDlg = wx.FileDialog(self, 'Choose a file',
                                        self.schemadirname, '', '*.csv;', wx.FD_SAVE)
            if saveDlg.ShowModal() == wx.ID_OK:
                self.schemafilename = saveDlg.GetFilename()
                self.schemadirname = saveDlg.GetDirectory()
                try:
                    data.to_csv(os.path.join(self.schemadirname, self.schemafilename), index=False)
                except:
                    alertdialog = wx.MessageDialog(self, 'An error occurred. Cannot save a scheme to disk.')
                    alertdialog.ShowModal()
            saveDlg.Destroy()

        fileMenu = wx.Menu()
        menuImport = fileMenu.Append(wx.NewId(), "&Import", "Import scheme")
        menuSave = fileMenu.Append(wx.NewId(), "&Save", "Save scheme")
        menuSaveAs = fileMenu.Append(wx.NewId(), "S&ave As..", "Save scheme as..")
        menuExit = fileMenu.Append(wx.NewId(), "&Close", "Close")
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")

        dlg = wx.Frame(self, title='Edit Headers')
        dlg.SetMenuBar(menuBar)
        dlg.Bind(wx.EVT_MENU, OnClose, menuExit)
        dlg.Bind(wx.EVT_MENU, lambda e: OnSaveAs(e, headdf), menuSaveAs)

        theList = wx.ListCtrl(dlg, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        dlg.Bind(wx.EVT_MENU, lambda e: OnImport(e, theList, headdf, columns), menuImport)
        if not self.schemafilename:  # new schema
            headdf = headdf.append(createNewHeaderSchemaList(theList, self.df, columns))
        dlg.Show()


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, "Armor v.%s" % VERSION)
    app.MainLoop()
