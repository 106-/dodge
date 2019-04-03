# -*- coding:utf-8 -*-

import math
import random
import time
from ctypes import cdll, create_string_buffer 

dx = cdll.LoadLibrary("DxLib_x64.dll")

class rotate_char:
    def __init__(self, x, y, char, entry, display, exit, range):
        self.cnt = 0

        self.entry = entry
        self.display = display
        self.exit = exit
        self.time_entry = self.entry
        self.time_display = self.entry + self.display
        self.time_exit = self.entry + self.display + self.exit

        self.range = range
        self.base_x = x
        self.base_y = y
        self.draw_x = x
        self.draw_y = y
        self.char = char
        self.expired = False
    
    def update(self):
        self.cnt += 1
        if(self.cnt < self.time_entry):
            ratio = (float(self.cnt)/float(self.entry))
            self.draw_x, self.draw_y = self.__calcpos(ratio)

        elif(self.time_entry <= self.cnt <= self.time_display):
            self.draw_x = self.base_x
            self.draw_y = self.base_y

        elif(self.time_display < self.cnt < self.time_exit):
            ratio = (float(self.cnt-self.time_display)/float(self.exit))
            self.draw_x, self.draw_y = self.__calcpos(1-ratio)

        else:
            self.expired = True
    
    def draw(self):
        dx.dx_DrawString(int(self.draw_x), int(self.draw_y), self.char, dx.dx_GetColor(255,255,255), 0)

    def __calcpos(self, ratio):
        angle = (1-ratio)*2*math.pi
        rang = (1-ratio)*self.range
        x = self.base_x + math.cos(angle)*rang
        y = self.base_y + math.sin(angle)*rang
        return x, y

class rotate_string:
    """
    ぐるぐるする文字列

    x,y :
        座標
    string :
        文字列
    entry :
        入ってくるときのぐるぐるにかかる時間
    display :
        文字列が止まる時間
    exit :
        出ていくときのぐるぐるにかかる時間
    range :
        ぐるぐるの基本的な幅
    gap :
        rangeからずらす範囲
    """
    def __init__(self, x, y, string, entry, display, exit, interval, range, gap_range):
        self.cnt = 0

        self.x = x
        self.y = y
        self.string = string
        self.entry = entry
        self.display = display
        self.exit = exit
        self.interval = interval
        self.range = range
        self.gap_range = gap_range

        self.remain_string = string
        self.charlst = []
    
    def update(self):
        if(self.cnt % self.interval == 0 and self.remain_string != ''):
            idx = len(self.string)-len(self.remain_string)
            char_width = dx.dx_GetDrawStringWidth("A", 1 ) 
            #rangeからのズレを計算する
            r = random.randrange(self.range-self.gap_range, self.range+self.gap_range)
            self.charlst.append(rotate_char(self.x+idx*char_width, self.y, self.remain_string[0], self.entry, self.display, self.exit, r))
            self.remain_string = self.remain_string[1:]
        self.cnt += 1
        for i in self.charlst:
            i.update()
            if(i.expired):
                self.charlst.remove(i)

    def draw(self):
        for i in self.charlst:
            i.draw()

class showfps:
    """
    fpsを表示するオブジェクト
    x,y : 表示する座標
    """
    def __init__(self, x, y):
        self.fps = 0
        self.x = x
        self.y = y
        self.interval = 100
        self.cnt = 0
        self.old_time = time.time()
    
    def update(self):
        self.cnt += 1
        if(self.cnt % self.interval == 0):
            now_time = time.time()
            delta = now_time - self.old_time
            if delta == 0:
                self.fps = 0
            else:
                self.fps = float(self.interval) / delta
            self.old_time = now_time
            
    def draw(self):
        dx.dx_DrawString(int(self.x), int(self.y), to_strbuf("fps:%.2f"%self.fps), dx.dx_GetColor(255,255,255), 0)        

class CheckButton:
    def __init__(self, buttons):
        self.buttons = buttons
        self.key = {}
        for i in self.buttons:
            self.key[i] = 0
    
    def update(self):
        for i in self.buttons:
            if dx.dx_CheckHitKey(i):
                self.key[i] += 1
            else:
                self.key[i] = 0

def to_strbuf(string):
    return create_string_buffer(string.encode("utf-8"))