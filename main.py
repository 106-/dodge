# -*- coding:utf-8 -*-

import math
import random
import sys
import agent
from gamelib import *
from dodge import dodge

WIDTH = 500 
HEIGHT = 600

def main():
    dx.dx_ChangeWindowMode(1)
    dx.dx_SetGraphMode(WIDTH, HEIGHT, 32)
    dx.dx_SetMainWindowText(to_strbuf("dodge"))
    if(dx.dx_DxLib_Init() == -1 or dx.dx_SetDrawScreen(-2) !=0 ):
        sys.exit()

    handler = agent.HumanHandler

    fps = showfps(0, HEIGHT-15)
    dodge_ins = dodge()
    ag = agent.Agent(dodge_ins, handler)

    cnt = 0
    while dx.dx_ProcessMessage() == 0:
        dx.dx_DrawBox(0, 0, WIDTH, HEIGHT, dx.dx_GetColor(0, 0, 0), 1)

        dodge_ins.update()
        ag.update()
        fps.update()
        
        dodge_ins.draw()
        ag.draw()
        fps.draw()

        if ag.isdead:
            dodge_ins = dodge()
            ag = agent.Agent(dodge_ins, handler)

        dx.dx_ScreenFlip()
        cnt += 1
    dx.dx_DxLib_End()

if(__name__=='__main__'):
    main()