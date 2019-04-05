
from gamelib import CheckButton, dx, to_strbuf
from dodge import block_center, block_size
import numpy as np
from main import HEIGHT
from sprites import sprites
from dodge import dodge

LEFT = 203
RIGHT = 205

class Agent:

    def __init__(self, dodge, handler):
        self.pos = block_center
        self.isdead = False
        self.dodge = dodge
        self.handler = handler
        self.handler.set_agent(self)

    def update(self):
        self.check_collision()
        self.handler.update()

    def check_collision(self):
        if self.dodge.collision(self.pos):
            self.isdead = True

    def draw(self):
        self.handler.draw()
        self.check_collision()
        if not self.isdead:
            pos = dodge.convert_pos(self.pos, 1)
            self.dodge.draw_block(self.pos, 1, color=dx.dx_GetColor(0, 255, 255))
            dx.dx_DrawGraph(pos[0], pos[1], sprites().CAT)

class HumanHandler:
    # これら数字はdxlibのdefineによる
    LEFT = 203
    RIGHT = 205

    def __init__(self):
        self.button = CheckButton([HumanHandler.LEFT, HumanHandler.RIGHT])
        self.agent = None
    
    def set_agent(self, agent):
        self.agent = agent

    def update(self):
        self.button.update()
        if self.button.key[HumanHandler.LEFT] == 1:
            self.agent.pos -= 1
        if self.button.key[HumanHandler.RIGHT] == 1:
            self.agent.pos += 1
    
    def draw(self):
        pass

class QTableHandler:
    LEFT = 0
    STAY = 1
    RIGHT = 2

    def __init__(self, old_q_table=None, cum_reward=0):
        # 行動逆温度
        self.epsilon = 0.1
        # 割引率
        self.gamma = 0.9
        # 減速パラメータ
        self.alpha = 0.1

        if not old_q_table is None:
            self.q_table = old_q_table
        else:
            self.q_table = np.random.rand(2**24, 3)
        self.agent = None
        self.old_sight = None
        self.old_act = None
        self.cum_reward = cum_reward
    
    def set_agent(self, agent):
        self.agent = agent

    def update(self):

        sight = self.agent.dodge.get_sight(self.agent.pos)
        # 前回の行動の評価
        if self.old_sight:
            reward = 0
            if self.agent.isdead:
                reward = -100
            else:
                sight = self.agent.dodge.get_sight(self.agent.pos, vector=True)[:4]
                # 生存ボーナス
                reward += 5
                # 壁に近いほど報酬を下げる
                reward += np.dot(sight, [-10, -20, -20, -10])
            self.cum_reward += reward
            sight_next = np.array([self.agent.dodge.get_sight(self.agent.pos-1),
                                    self.agent.dodge.get_sight(self.agent.pos),
                                    self.agent.dodge.get_sight(self.agent.pos+1)])
            next_q_max = np.max(self.q_table[sight_next])
            self.q_table[self.old_sight][self.old_act] += self.alpha * ( reward + self.gamma * next_q_max - self.q_table[self.old_sight][self.old_act] )

        self.old_sight = self.agent.dodge.get_sight(self.agent.pos)

        # 行動
        act = None
        if np.random.rand() < self.epsilon:
            act = np.random.choice([QTableHandler.LEFT, QTableHandler.STAY, QTableHandler.RIGHT])
        else:
            sight = self.agent.dodge.get_sight(self.agent.pos)
            q = self.q_table[sight]
            act = np.argmax(q)
        
        if act == QTableHandler.LEFT:
            self.agent.pos -= 1
        elif act == QTableHandler.RIGHT:
            self.agent.pos += 1
        
        self.old_act = act
    
    def draw(self):
        dx.dx_DrawString(0, 30, to_strbuf("reward: %d"%self.cum_reward), dx.dx_GetColor(255,255,255), 0)        