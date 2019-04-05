
import numpy as np
from gamelib import dx
from sprites import sprites

terrain_height = 600
terrain_width = 500
block_size = 20 
block_num_x = int(terrain_width / block_size)
block_num_y = int(terrain_height / block_size)
block_center = int(block_num_x / 2)
block_length_min = 30
block_length_max = 60

class dodge:
    def __init__(self):
        self.cnt = 0
        self.terrain = obstacle.make_obstacle( block_center, block_center, block_num_y)
        self.latest_obs_length = 10
        self.latest_obs_cnt = 0
        self.latest_obs_center = block_center
        self.terrain = np.vstack((self.terrain, obstacle.make_obstacle( block_center, block_center, self.latest_obs_length) ))
        
        self.sight_filter = np.full(24, 2)
        self.sight_filter = np.power(self.sight_filter, np.arange(24))

    def update(self):
        self.terrain = np.delete(self.terrain, 0, axis=0)

        if self.latest_obs_length - (self.cnt - self.latest_obs_cnt) == 0:
            self.latest_obs_cnt = self.cnt
            self.latest_obs_length = np.random.randint(block_length_min, block_length_max+1)
            center = np.random.randint(0, len(self.terrain[0]))
            obs = obstacle.make_obstacle(self.latest_obs_center, center, self.latest_obs_length)
            self.terrain = np.vstack((self.terrain, obs)) 
            self.latest_obs_center = center

        self.cnt += 1
    
    def draw(self):
        for y in range(block_num_y):
            for x in range(block_num_x):
                if self.terrain[y][x] == 1:
                    self.draw_block(x, y)

    def draw_block(self, x, y, color=dx.dx_GetColor(255, 0, 0)):
        pos = dodge.convert_pos(x, y)
        dx.dx_DrawBox(block_size*x, terrain_height-block_size*(y+1), block_size*(x+1)-1, terrain_height-block_size*y-1, color, 1)
    
    @staticmethod
    def convert_pos(x, y):
        return (block_size*x, terrain_height-block_size*(y+1))

    def collision(self, pos):
        return pos < 0 or block_num_x-1 < pos or self.terrain[1][pos] == 1
    
    def get_sight(self, pos, vector=False):
        # 前方5マスのブロック情報を取得
        # ■ ■ ■ □ □
        # ■ ■ ■ □ □
        # □ ■ □ □ □
        # □ □ □ □ □
        # □ □ × □ □
        sight = np.ones((5, 5))
        if pos-2 < 0:
            sight_start = 0
            gap_start = abs(pos-2)
        else:
            sight_start = pos-2
            gap_start = 0
        
        if block_num_x < pos+3:
            sight_end = block_num_x
            gap_end = 5-abs(pos+3-block_num_x)
        else:
            sight_end = pos+3
            gap_end = 5
        sight[0:, gap_start:gap_end] = self.terrain[1:6,sight_start:sight_end]
        # 自機マスの削除
        sight = np.delete(sight.flatten(), 2)
        if vector:
            return sight
        else:
            return int(np.dot(sight, self.sight_filter))

class obstacle:
    passage_width = 4

    def linear( start, end, length):
        return np.array([ int(start+0.5 + ( end - start ) * (t / length)) for t in range(length)])

    @classmethod
    def make_obstacle(cls, start, end, length, func=linear):
        obs = np.ones((length, block_num_x))
        center_line = func(start, end, length)
        for i, o in enumerate(obs):
            passage_edge = np.clip([center_line[i] - cls.passage_width , center_line[i] + cls.passage_width], 0, block_num_x)
            obs[i][passage_edge[0]:passage_edge[1]] = 0
        return obs