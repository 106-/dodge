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

    # handler = agent.HumanHandler
    # handler = agent.QTableHandler()
    handler = agent.QModelHandler(sight_range=9)

    score = 0
    hi_score = 0
    fps = showfps(0, 0)
    dodge_ins = dodge()
    ag = agent.Agent(dodge_ins, handler)
    episode = 1

    cnt = 0
    while dx.dx_ProcessMessage() == 0:
        dx.dx_DrawBox(0, 0, WIDTH, HEIGHT, dx.dx_GetColor(0, 0, 0), 1)

        score += 1
        if score >= hi_score:
            hi_score = score

        dodge_ins.update()
        ag.update()
        fps.update()
        
        dodge_ins.draw()
        ag.draw()
        fps.draw()
        dx.dx_DrawString(0, 15, to_strbuf("episode: %d"%episode), dx.dx_GetColor(255,255,255), 0)        
        dx.dx_DrawString(0, 30, to_strbuf("SCORE: %d"%score), dx.dx_GetColor(255,255,255), 0)        
        dx.dx_DrawString(0, 45, to_strbuf("HI-SCORE: %d"%hi_score), dx.dx_GetColor(255,255,255), 0)        

        if ag.isdead:
            dodge_ins = dodge()
            handler.set_agent(ag)
            ag = agent.Agent(dodge_ins, handler)
            score = 0
            episode += 1

        dx.dx_ScreenFlip()
        cnt += 1
    dx.dx_DxLib_End()

if(__name__=='__main__'):
    main()