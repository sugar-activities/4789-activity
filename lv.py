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

class Listview(): 
    def __init__(self, name, items, cb):
        
        vbox = Gtk.VBox()
        vbox.set_size_request(640,480)
        sw = Gtk.ScrolledWindow()
        #sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        #sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        vbox.pack_start(sw, True, True, 0)

        store = self.create_model(items)

        treeView = Gtk.TreeView(store)
        treeView.connect("row-activated", cb)
        treeView.set_rules_hint(True)
        sw.add(treeView)

        self.create_columns(treeView, name)
        self.statusbar = Gtk.Statusbar()
        
        vbox.pack_start(self.statusbar, False, False, 0)
        self.vbox = vbox


    def create_model(self, items):
            
        store = Gtk.ListStore(str)
        for item in items:
           store.append([item])
        return store


    def create_columns(self, treeView, name):
    
        rendererText = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn(name, rendererText, text=0)
        column.set_sort_column_id(0)    
        treeView.append_column(column)
        


