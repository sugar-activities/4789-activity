#!/usr/bin/python

# ZetCode PyGTK tutorial 
#
# This example shows a TreeView widget
# in a list view mode
#
# author: jan bodnar
# website: zetcode.com 
# last edited: February 2009


from gi.repository import Gtk



class Languages(): 
    def __init__(self, langs):

        vbox = Gtk.VBox(False, 8)

        self.text = ''
        
        sw = Gtk.ScrolledWindow()
        
        vbox.pack_start(sw, True, True, 0)

        store = self.create_model(langs)

        treeView = Gtk.TreeView(store)
        treeView.connect("row-activated", self.on_activated)
        treeView.set_rules_hint(True)
        sw.add(treeView)

        self.create_columns(treeView)
        self.statusbar = Gtk.Statusbar()
        self.statusbar.push(0, 'Hello World')
        
        vbox.pack_start(self.statusbar, False, False, 0)

        self.vbox = vbox


    def create_model(self, langs):
        store = Gtk.ListStore(str)

        for lang in langs:
            store.append([lang])

        return store


    def create_columns(self, treeView):
    
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Language", rendererText, text=0)
        column.set_sort_column_id(0)    
        treeView.append_column(column)

    def on_activated(self, widget, row, col):
        
        model = widget.get_model()
        text = model[row][0]
        print text
        self.selected_lang = text

