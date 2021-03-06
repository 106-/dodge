
from gamelib import CheckButton, dx, to_strbuf
from dodge import block_center, block_size
import numpy as np
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
        if hasattr(self.handler, "set_agent"):
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
        # 貪欲/挑戦の調整パラメータ betaが高いほど貪欲志向, Noneで無限大
        self.beta = None

        self.agent = None
        self.cum_reward = cum_reward
    
    def set_agent(self, agent):
        self.agent = agent

    def update(self):
        pass

    def draw(self):
        dx.dx_DrawString(0, 60, to_strbuf("reward: %d"%self.cum_reward), dx.dx_GetColor(255,255,255), 0)        

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
            sight = self.agent.dodge.get_sight(self.agent.pos, number=True)
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
    def __init__(self, cum_reward=0, model=False, sight_range=5):

        if sight_range % 2 == 0:
            raise ValueError("sight_range must be odd number.")
        self.sight_range = sight_range

        self.old_sight = None
        self.old_act = None
        
        if model is False:
            self.model = Sequential()
            self.model.add(Dense(3, activation='linear', input_dim=self.sight_range**2-1))
            self.model.compile(loss=mean_squared_error, optimizer=Adamax())
        else:
            self.model = model
    
        super().__init__(cum_reward)
    
    def _softmax(self, energy):
        energy_exp = np.exp(energy)
        return energy_exp / np.sum(energy_exp)  

    def update(self):
        if not (self.old_sight is None):
            reward = 0
            if self.agent.isdead:
                reward = -100
            else:
                sight = self.agent.dodge.get_sight(self.agent.pos, sight_range=self.sight_range)[:self.sight_range-1]
                # 生存ボーナス
                reward += 5 
                # 壁に近いほど報酬を下げる
                penalty = np.linspace(-5, -50, (self.sight_range-1)/2 ) 
                reward += np.dot(sight, np.hstack((penalty, penalty[::-1])))
            self.cum_reward += reward
            
            sight = self.agent.dodge.get_sight(self.agent.pos, sight_range=self.sight_range).reshape(1,self.sight_range**2-1)
            if self.beta == None:
                next_q = np.max(self.model.predict(sight))
            else:
                now_q = self.model.predict(sight)
                next_q = np.sum(self._softmax(self.beta * now_q) * now_q)
            # 一つ前の状態のq値
            target_q = self.model.predict(self.old_sight)
            target_q_value = target_q[0][self.old_act] + self.alpha * ( reward + self.gamma * next_q - target_q[0][self.old_act] )
            target_q[0][self.old_act] = target_q_value

            self.model.fit(self.old_sight, target_q, verbose=0)

        self.old_sight = self.agent.dodge.get_sight(self.agent.pos, sight_range=self.sight_range).reshape(1,self.sight_range**2-1)

        # 行動
        act = None
        if np.random.rand() < self.epsilon:
            act = np.random.choice([QTableHandler.LEFT, QTableHandler.STAY, QTableHandler.RIGHT])
        else:
            sight = self.agent.dodge.get_sight(self.agent.pos, sight_range=self.sight_range).reshape(1,self.sight_range**2-1)
            q = self.model.predict(sight)
            act = np.argmax(q)
        
        if act == QTableHandler.LEFT:
            self.agent.pos -= 1
        elif act == QTableHandler.RIGHT:
            self.agent.pos += 1
        
        self.old_act = act
    
    def draw(self):
        dx.dx_SetDrawBlendMode(1, 128)
        center = int((self.sight_range-1)/2)
        for y in range(1, self.sight_range+1):
            for x in range(self.agent.pos-center, self.agent.pos+(self.sight_range-center)):
                self.agent.dodge.draw_block(x, y, color=dx.dx_GetColor(0, 0, 255))
        dx.dx_SetDrawBlendMode(0, 0)
        super().draw()

from keras.models import load_model
import math

class QSavedModelHandler:
    def __init__(self, filename):
        self.model = load_model(filename)
        input_dim = self.model.get_layer(index=0).get_weights()[0].shape[0]
        self.sight_range = int(math.sqrt(input_dim+1))
    
    def set_agent(self, agent):
        self.agent = agent

    def update(self):
        sight = self.agent.dodge.get_sight(self.agent.pos, sight_range=self.sight_range).reshape(1,self.sight_range**2-1)
        q = self.model.predict(sight)
        act = np.argmax(q)
        
        if act == QTableHandler.LEFT:
            self.agent.pos -= 1
        elif act == QTableHandler.RIGHT:
            self.agent.pos += 1
    
    def draw(self):
        pass