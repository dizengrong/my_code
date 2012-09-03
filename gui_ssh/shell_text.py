# -*- coding: utf8 -*-
from Tkinter import *

class ShellText(Text):
    def __init__(self, master, prefix, height = 25, width = 80, yscrollcommand = None):
        Text.__init__(self, master)
        self.bind('<Key>', self.insert_char)
        self.bind('<Return>', self.insert_return)
        self.bind('<Button-1>', self.left_mouse_click)
        self.set_prefix(prefix)

    def set_cmd_callback(self, callback):
        self.callback = callback

    def get_cmd(self):
        print('cmd begin: %s, end: %s' % (self.index('CMD_BEGIN'), self.index(INSERT)))
        return self.get('CMD_BEGIN', INSERT)

    def set_prefix(self, prefix):
    	self.prefix = prefix
    	self.insert(END, prefix)
        self.mark_set('CMD_BEGIN', INSERT)
        self.mark_gravity("CMD_BEGIN", LEFT)

    def insert_char(self, event):
    	print('pressed char key code is: %s' % event.keycode)
    	if event.keycode == 37:    # 向左的箭头
    		return 'break'

    def insert_return(self, event):
        cmd = self.get_cmd()
        out_str = self.callback(cmd)
        print('cmd: %s' % cmd)
    	self.insert(END, '\n' + self.prefix + out_str)
        self.mark_set('CMD_BEGIN', INSERT)
        self.mark_gravity("CMD_BEGIN", LEFT)
    	return 'break'

    def left_mouse_click(self, event):
    	print('left mouse click, x: %d, y: %d' % (event.x, event.y))
    	# return 'break'	

