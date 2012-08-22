# -*- coding: utf8 -*-
from Tkinter import *
import os

class Application(Frame):
    def cmd_get_lastest_datas(self):
        os.system('fab get_lastest_datas')

    def cmd_status(self):
        os.system('fab get_status')

    def cmd_start(self):
        os.system('fab start')

    def cmd_stop(self):
        os.system('fab stop')

    def createWidgets(self):
        self.status = Button(self)
        self.status["text"] = u"获取服务器状态"
        self.status["command"] =  self.cmd_status

        self.status.pack({"side": "left"})

        self.start = Button(self)
        self.start["text"] = u"启动服务",
        self.start["command"] = self.cmd_start

        self.start.pack({"side": "left"})

        self.stop = Button(self)
        self.stop["text"] = u"停止服务",
        self.stop["command"] = self.cmd_stop

        self.stop.pack({"side": "right"})

        self.lastest_datas = Button(self)
        self.lastest_datas["text"] = u"获取最新配置数据",
        self.lastest_datas["command"] = self.cmd_get_lastest_datas

        self.lastest_datas.pack({"side": "right"})


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

root = Tk()
root.title(u'服务器管理')
app = Application(master=root)
app.mainloop()
root.destroy()