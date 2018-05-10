import os
import json
import wx
import pandas as pd
from collections import defaultdict
from components.gridtable import DataGrid, DataTable

VERSION = "0.1"


class SchemaDialog(wx.Dialog):
    def __init__(self, item, unique_values):
        wx.Dialog.__init__(self, None, -1, "Schema Setup")
        about = wx.StaticText(self, -1, "Please edit information below.")
        header = wx.StaticText(self, -1, "Header: %s" % item['header'])
        mapper = wx.StaticText(self, -1, "Mapper:")
        uvalue = wx.StaticText(self, -1, "Unique values:")

        self.mapper_t = wx.TextCtrl(self, -1, item['mapper'])
        self.drug_t = wx.CheckBox(self, -1, "Drug")
        self.exclude_t = wx.CheckBox(self, -1, "Exclude")
        self.values_t = wx.CheckListBox(self, -1, choices=unique_values)
        ok = wx.Button(self, wx.ID_OK)
        ok.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(about)
        sizer.Add(wx.StaticLine(self))
        fgs = wx.GridBagSizer(vgap=5, hgap=5)
        fgs.Add(header, (1,1), (1,2), wx.EXPAND)
        fgs.Add(mapper, (2,1))
        fgs.Add(self.mapper_t, (2,2))
        fgs.Add(self.drug_t, (3,1))
        fgs.Add(self.exclude_t, (3,2))
        sizer.Add(fgs)
        sizer.Add(wx.StaticLine(self))
        sizer.Add(uvalue)
        sizer.Add(self.values_t, 0, wx.EXPAND)

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(ok)
        btns.AddButton(cancel)
        btns.Realize()
        sizer.Add(btns, 0, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)


class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MainFrame, self).__init__(parent=parent, title=title)
        helpmenu = wx.Menu()
        filemenu = wx.Menu()
        gridmenu = wx.Menu()
        menuExit = filemenu.Append(wx.ID_EXIT, "E&xit", "Exit the program.")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About", "About the program.")
        menuImport = gridmenu.Append(wx.ID_OPEN, "&Import", "Import data to a grid.")
        menuSumGrid = gridmenu.Append(wx.ID_PREVIEW, "View Summary", "Summarize data.")
        menuEditHeaderGrid = gridmenu.Append(wx.ID_EDIT, "Set Schema", "Set a schema for the data.")
        menuCloseGrid = gridmenu.Append(wx.ID_CLOSE, "Close", "Close the opened grid.")

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
            self.schemafilename = ''

    def OnSumGrid(self, e):
        childFrame = wx.Frame(self, title="Description")
        self.desgrid = DataGrid(childFrame, data=self.df.describe())
        childFrame.Show()

    def OnEditHeaderGrid(self, e):

        columns = ['header', 'mapper', 'dtype', 'drug', 'include', 'filter']
        headdf = {}

        def createNewHeaderSchemaList(theList, dataframe, columns):
            headerdata = defaultdict(list)
            dtypes = dataframe.dtypes
            theList.InsertColumn(0, "No.")
            for col, text in enumerate(columns, start=1):
                theList.InsertColumn(col, text)

            for idx, header in enumerate(dataframe.columns):
                index = theList.InsertStringItem(idx, str(idx+1))
                theList.SetStringItem(index, 1, header)
                theList.SetStringItem(index, 2, header)
                theList.SetStringItem(index, 3, str(dtypes[header]))
                headerdata["header"].append(header)
                headerdata["dtype"].append(str(dtypes[header]))
                headerdata["mapper"].append(header)
                headerdata["drug"].append(False)
                headerdata["include"].append(True)
                headerdata["filter"].append({header: []})

            theList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(3, wx.LIST_AUTOSIZE)
            return pd.DataFrame(headerdata)

        def createHeaderSchemaListFromFile(theList, dataframe, columns):
            theList.ClearAll()
            for col, text in enumerate(columns):
                theList.InsertColumn(col, text)

            for idx in range(len(dataframe[columns[0]])):
                index = theList.InsertStringItem(idx, str(idx+1))
                for n, colname in enumerate(columns):
                    theList.SetStringItem(index, n+1, str(dataframe[colname][idx]))

            theList.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            theList.SetColumnWidth(3, wx.LIST_AUTOSIZE)

        def OnItemSelected(event, headdf, data):
            row = event.GetIndex()
            item = headdf.iloc[row]
            unique_values = [u'{}'.format(value) for value in data[item['header']].unique()]
            dlg = SchemaDialog(item, unique_values)
            if dlg.ShowModal() == wx.ID_OK:
                mapper = dlg.mapper_t.Value
                drug = dlg.drug_t.Value
                excluded = dlg.exclude_t.Value
                headdf.at[row, 'mapper'] = mapper
                headdf.at[row, 'drug'] = drug
                headdf.at[row, 'include'] = excluded
            dlg.Destroy()
            print(headdf.iloc[row])
            theList = event.GetEventObject()
            theList.SetStringItem(row, 2, mapper)
            if drug:
                theList.SetStringItem(row, 4, str(drug))
            if excluded:
                theList.SetStringItem(row, 5, str(False))  # not included


        def OnLoad(event, theList, dataframe, columns):
            openDlg = wx.FileDialog(self, 'Choose a file', self.schemadirname, '', '*.json;', wx.FD_OPEN)
            if openDlg.ShowModal() == wx.ID_OK:
                self.schemafilename = openDlg.GetFilename()
                self.schemadirname = openDlg.GetDirectory()
                try:
                    with open(os.path.join(self.schemadirname, self.schemafilename), 'rb') as fp:
                        dataframe = json.load(fp)
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
            if not self.schemafilename:  # the schema has never been saved before
                OnSaveAs(event, data)
            else:
                try:
                    with open(os.path.join(self.schemadirname, self.schemafilename), 'w') as fp:
                        json.dump(data, fp, indent=True)
                except:
                    alertdialog = wx.MessageDialog(self,
                                        'An error occurred. Cannot save a schema to disk.')

        def OnClose(event):
            dlg.Hide()

        def OnSaveAs(event, data):
            saveDlg = wx.FileDialog(self, 'Choose a file',
                                        self.schemadirname, '', '*.json;', wx.FD_SAVE)
            if saveDlg.ShowModal() == wx.ID_OK:
                self.schemafilename = saveDlg.GetFilename()
                self.schemadirname = saveDlg.GetDirectory()
                try:
                    with open(os.path.join(self.schemadirname, self.schemafilename), 'w') as fp:
                        json.dump(data, fp, indent=True)
                except Exception as e:
                    alertdialog = wx.MessageDialog(self, 'An error occurred. Cannot save a schema to disk.')
                    alertdialog.ShowModal()
            saveDlg.Destroy()

        fileMenu = wx.Menu()
        menuLoad = fileMenu.Append(wx.NewId(), "&Load Schema", "Load a schema from a file.")
        menuApply = fileMenu.Append(wx.NewId(), "&Apply Schema", "Apply this schema to this dataset.")
        menuSave = fileMenu.Append(wx.NewId(), "&Save Schema", "Save this schema to a file.")
        menuSaveAs = fileMenu.Append(wx.NewId(), "S&ave Schema As..",
                                        "Save this schema a new file.")
        menuExit = fileMenu.Append(wx.NewId(), "&Close Window", "Close the window.")
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&Action")

        dlg = wx.Frame(self, title='Schema Manager')
        dlg.CreateStatusBar(1)
        dlg.SetMenuBar(menuBar)
        dlg.Bind(wx.EVT_MENU, OnClose, menuExit)
        dlg.Bind(wx.EVT_MENU, lambda e: OnSaveAs(e, headdf), menuSaveAs)

        theList = wx.ListCtrl(dlg, -1, style=wx.LC_REPORT|wx.LC_HRULES|wx.LC_VRULES)
        dlg.Bind(wx.EVT_MENU, lambda e: OnLoad(e, theList, headdf, columns), menuLoad)
        if not self.schemafilename:  # new schema
            headdf = createNewHeaderSchemaList(theList, self.df, columns)
        dlg.Show()
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, lambda e: OnItemSelected(e, headdf, self.df), theList)


if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame(None, "Armor v.%s" % VERSION)
    app.MainLoop()
