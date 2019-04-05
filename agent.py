
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

class QLearningHandler:
    LEFT = 0
    STAY = 1
    RIGHT = 2

    def __init__(self, cum_reward=0):
        # 行動逆温度
        self.epsilon = 0.1
        # 割引率
        self.gamma = 0.9
        # 減速パラメータ
        self.alpha = 0.1

        self.agent = None
        self.cum_reward = cum_reward
    
    def set_agent(self, agent):
        self.agent = agent

    def update(self):
        pass

    def draw(self):
        dx.dx_DrawString(0, 30, to_strbuf("reward: %d"%self.cum_reward), dx.dx_GetColor(255,255,255), 0)        

class QTableHandler(QLearningHandler):
    def __init__(self, cum_reward=0, old_q_table=False):
        self.old_sight = None
        self.old_act = None
        
        if old_q_table is False:
            self.q_table = np.random.rand(2**24, 3)
        else:
            self.q_table = old_q_table

        super().__init__(cum_reward)
    
    def update(self):
        # 前回の行動の評価
        if self.old_sight:
            reward = 0
            if self.agent.isdead:
                reward = -100
            else:
                sight = self.agent.dodge.get_sight(self.agent.pos)[:4]
                # 生存ボーナス
                reward += 5
                # 壁に近いほど報酬を下げる
                reward += np.dot(sight, [-10, -20, -20, -10])
            self.cum_reward += reward
            sight = self.agent.dodge.get_sight(self.agent.pos, number=True)
            next_q_max = np.max(self.q_table[sight])
            self.q_table[self.old_sight][self.old_act] += self.alpha * ( reward + self.gamma * next_q_max - self.q_table[self.old_sight][self.old_act] )

        self.old_sight = self.agent.dodge.get_sight(self.agent.pos, number=True)

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

from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adamax
from keras.losses import mean_squared_error

class QModelHandler(QLearningHandler):
    def __init__(self, cum_reward=0, model=False):
        self.old_sight = None
        self.old_act = None
        
        if model is False:
            self.model = Sequential()
            self.model.add(Dense(3, activation='linear', input_dim=24))
            self.model.compile(loss=mean_squared_error, optimizer=Adamax())
        else:
            self.model = model
    
        super().__init__(cum_reward)
    
    def update(self):
        if not (self.old_sight is None):
            reward = 0
            if self.agent.isdead:
                reward = -100
            else:
                sight = self.agent.dodge.get_sight(self.agent.pos)[:4]
                # 生存ボーナス
                reward += 5
                # 壁に近いほど報酬を下げる
                reward += np.dot(sight, [-10, -20, -20, -10])
            self.cum_reward += reward
            
            sight = self.agent.dodge.get_sight(self.agent.pos).reshape(1,24)
            next_q_max = np.max(self.model.predict(sight))
            # 一つ前の状態のq値
            target_q = self.model.predict(self.old_sight)
            target_q_value = target_q[0][self.old_act] + self.alpha * ( reward + self.gamma * next_q_max - target_q[0][self.old_act] )
            target_q[0][self.old_act] = target_q_value

            self.model.fit(self.old_sight, target_q, verbose=0)

        self.old_sight = self.agent.dodge.get_sight(self.agent.pos).reshape(1,24)

        # 行動
        act = None
        if np.random.rand() < self.epsilon:
            act = np.random.choice([QTableHandler.LEFT, QTableHandler.STAY, QTableHandler.RIGHT])
        else:
            sight = self.agent.dodge.get_sight(self.agent.pos).reshape(1,24)
            q = self.model.predict(sight)
            act = np.argmax(q)
        
        if act == QTableHandler.LEFT:
            self.agent.pos -= 1
        elif act == QTableHandler.RIGHT:
            self.agent.pos += 1
        
        self.old_act = act