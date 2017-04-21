# Copyright 2009 Simon Schampijer
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""HelloWorld Activity: A case study for developing an activity."""

import sys,time
from gi.repository import Gtk
from gi.repository import Gdk
import logging

from gettext import gettext as _

from sugar3.activity import activity
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.activity.widgets import ActivityButton
from sugar3.activity.widgets import TitleEntry
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ShareButton
from sugar3.activity.widgets import DescriptionItem

from path import path
from subprocess import call, Popen, PIPE
from lv import Listview

class LionActivity(activity.Activity):
    """HelloWorldActivity class as specified in activity.info"""

    def __init__(self, handle):
        """Set up the HelloWorld activity."""
        activity.Activity.__init__(self, handle)

        # we do not have collaboration features
        # make the share option insensitive
        self.max_participants = 1

        # toolbar with the new toolbar redesign
        toolbar_box = ToolbarBox()

        activity_button = ActivityButton(self)
        toolbar_box.toolbar.insert(activity_button, 0)
        activity_button.show()

        title_entry = TitleEntry(self)
        toolbar_box.toolbar.insert(title_entry, -1)
        title_entry.show()

        description_item = DescriptionItem(self)
        toolbar_box.toolbar.insert(description_item, -1)
        description_item.show()

        share_button = ShareButton(self)
        toolbar_box.toolbar.insert(share_button, -1)
        share_button.show()
        
        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbar_box.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        toolbar_box.toolbar.insert(stop_button, -1)
        stop_button.show()

        self.set_toolbar_box(toolbar_box)
        toolbar_box.show()

        #set background color
        self.override_background_color(Gtk.StateType.NORMAL, Gdk.RGBA(1.0,1.0,0.0,1.0))
        #set up screen
        fix = Gtk.Fixed()
        fix.set_size_request(1000,750)
        self.lang = Gtk.Label('Language')
        fix.put(self.lang, 100,0)
        self.activity = Gtk.Label('Activity')
        fix.put(self.activity, 500, 0)
        self.fix = fix
        
        #initialize listview
        #display list of languages as listview
        items  = path('/usr/share/locale').dirs()
        locales = []
        for item in items:
            locales.append(item.namebase)
        locales.sort()
        self.languages = Listview('Language', locales, self.lang_cb)

        #get directories from /usr/share/locale
        vbox = self.languages.vbox
        self.fix.put(vbox, 100, 200)
        self.set_canvas(self.fix)
        self.fix.show_all()

    def lang_cb(self, widget, row, col):
        model = widget.get_model()
        self.lng = model[row][0]
        self.lang.set_markup('Language: <b>'+model[row][0]+'</b>')
        self.fix.remove(self.languages.vbox)

        #show list of activities
        items = path('/home/tony/Activities').dirs()
        #remove activities without po directory
        activities = []
        for item in items:
            pth = path(item) / 'po'
            if pth.exists():
                activities.append(item)
        activities.sort()
        #show activities in listview
        self.activities = Listview('Activity', activities, self.activity_cb)

        vbox = self.activities.vbox
        self.fix.put(vbox, 100, 100)
        self.set_canvas(self.fix)
        self.fix.show_all()

    def activity_cb(self, widget, row, col):
        model = widget.get_model()
        pth = path(model[row][0]).namebase
        self.activity.set_markup('Activity: <b>'+pth+'</b>')
        self.fix.remove(self.activities.vbox)
        #read po file
        #display string by string
        lng = self.lang.get_text()
        po = path(model[row][0]+'/po/'+self.lng+'.po')
        print 'po', po, po.exists()
        if not po.exists():
	    cmd = 'cp ' + str(pth).title() + '.pot ' + self.lng + '.po'
            print 'cmd', cmd
            print 'cwd', po.parent
            call(cmd, cwd=po.parent, shell=True)
        #get bundle_id
        fin = open(path(model[row][0]+'/activity/activity.info'),'r')
        txt = fin.read()
        fin.close()
        lines = txt.split('\n')
        for line in lines:
            if 'bundle_id' in line:
                pos = line.find('=')
                self.bundle_id = line[pos+1:].strip()
                break
        print 'bundle_id', self.bundle_id
        fin = open(po,'r')
        txt = fin.read()
        fin.close()
        lines = txt.split('\n')
        print 'po', po, str(len(lines))
        self.lines = lines
        self.make_screen()
        #process strings
        orig = path(po) + '.orig'
        if not orig.exists():
            cmd = 'cp '+po+' ' + orig
            call(cmd, shell=True)
        self.po = po
        fout = open(po,'w')
        self.fout = fout
        self.i = 0
        print 'lines', len(lines)
        #display initial screen
        self.show_screen()

    def show_screen(self):
        if self.i >= len(self.lines):
            self.cmntbfr.set_text('')
            self.msgidbfr.set_text('')
            self.msgstrbfr.set_text('')
        else:
            i, comment, msgid, msgstr = self.get_string()
            self.i = i
            self.cmntbfr.set_text(comment)
            self.msgidbfr.set_text(msgid)
            self.msgstrbfr.set_text(msgstr)
        self.set_canvas(self.fix)
        self.fix.show_all()

    def make_screen(self):
        label = Gtk.Label()
        label.set_markup('<b>Comment</b>')
        self.fix.put(label,0,20)
        cmnt = Gtk.TextView()
        self.cmntbfr = cmnt.get_buffer()
        self.cmntbfr.set_text('')
        cmnt.set_wrap_mode(True)
        cmnt.set_editable(False)
        cmnt.set_size_request(1000,150)
        self.fix.put(cmnt,0,50)
        label = Gtk.Label()
        label.set_markup('<b>Msgid</b>')
        self.fix.put(label,0,220)
        msgid = Gtk.TextView()
        self.msgidbfr = msgid.get_buffer()
        self.msgidbfr.set_text('')
        msgid.set_wrap_mode(True)
        msgid.set_editable(False)
        msgid.set_size_request(1000,150)
        self.fix.put(msgid,0,250)
        label = Gtk.Label()
        label.set_markup('<b>MsgStr</b>')
        self.fix.put(label,0,420)
        msgstr = Gtk.TextView()
        self.msgstrbfr = msgstr.get_buffer()
        self.msgstrbfr.set_text('')
        msgstr.set_wrap_mode(True)
        msgstr.set_editable(True)
        msgstr.set_size_request(1000,150)
        self.fix.put(msgstr,0,450)
        button = Gtk.Button.new_with_label('Accept')
        button.connect('clicked',self.on_accept)
        self.fix.put(button,0,650)

    def on_accept(self, widget):
        #write 'string' to output po file
        #write all lines to fout - except write modified 
        #msgstr lines - 80 characters per line, split at nearest space > 80
        fout = self.fout
        start = self.msgstrbfr.get_start_iter()
        end = self.msgstrbfr.get_end_iter()
        bfr = self.msgstrbfr.get_text(start,end, True)
        while len(bfr)>80:
            pos = bfr[80:].find(' ')
            print >> fout, bfr[:pos+80]
            bfr = bfr[80+pos+1:]
        print >> fout, bfr
        try:
            i = self.i + 1
            line = self.lines[i]
        except:
            self.fout.close()
            self.cmntbfr.set_text('Done')
            self.msgidbfr.set_text('')
            self.msgstrbfr.set_text('')
            self.set_canvas(self.fix)
            self.fix.show_all()
            #convert po to mo
            po_item = str(self.po)
            print type(po_item), po_item
            lang_item = self.lang
            print type(lang_item), lang_item
            bundle_item = self.bundle_id
            print type(bundle_item), bundle_item
            cmd = 'pocompile -i ' + str(self.po) + ' ' + '/usr/share/locale/' + str(self.lang) + '/LC_Messages/'+str(self.bundle_id)+'.mo'
            print 'pocompile', cmd
            #call(cmd, shell=True)
        else:
            print self.i, str(len(self.lines))
            self.show_screen()

    def get_string(self):
        i = self.i
        print 'get_string', str(i)
        lines = self.lines
        print 'source lines', len(lines)
        fout = self.fout
        if i == 0: #skip initial lines
            while lines[i]:
                line = lines[i]
                print >> fout, line
                i += 1
            print 'i after initial', i
        comment = ''
        msgid = ''
        msgstr = ''
        phase = 0
        line = lines[i]
        while phase == 0 and not 'msgid' in line:
            comment += line
            print >> fout, line
            i += 1
            line = lines[i]
        print 'comment',  str(i), comment
        phase = 1
        while phase == 1 and not 'msgstr' in line:
            msgid += line
            print >> fout, line
            i += 1
            line = lines[i]
        print 'msgid', str(i), msgid
        phase = 2
        while phase == 2 and line:
            msgstr += line
            i+= 1
            line = lines[i]
        print 'msgstr', str(i), msgstr
        return (i, comment, msgid, msgstr)            
