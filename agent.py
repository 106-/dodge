
from gamelib import CheckButton, dx
from dodge import block_center

LEFT = 203
RIGHT = 205

class Agent:

    def __init__(self, dodge, handler):
        self.pos = block_center
        self.isdead = False
        self.dodge = dodge
        self.handler = handler(self)

    def update(self):
        if self.dodge.collision_edge(self.pos):
            self.isdead = True
            return
        if self.dodge.collision(self.pos):
            self.isdead = True
            return
        # print(self.dodge.get_sight(self.pos))
        self.handler.update()

    def draw(self):
        self.dodge.draw_block(self.pos, 1, color=dx.dx_GetColor(0, 255, 255))
        self.handler.draw()

class HumanHandler:
    def __init__(self, agent):
        self.button = CheckButton([LEFT, RIGHT])
        self.agent = agent

    def update(self):
        self.button.update()
        if self.button.key[LEFT] == 1:
            self.agent.pos -= 1
        if self.button.key[RIGHT] == 1:
            self.agent.pos += 1
    
    def draw(self):
        pass

class QHandler:
    def __init__(self, agent):
        self.q_table = np.zeros((2, 25))
    
    def update(self):
        pass
    
    def draw(self):
        pass