# %% [markdown]
# 导入基本库

# %%
import cv2
import numpy as np
from PIL import Image
import time
import pickle
import matplotlib.pyplot as plt
from matplotlib import style
style.use('ggplot')

# %% [markdown]
# 基本参数

# %%
# 基本参数
SIZE = 10 # 场景范围
EPISODES = 30000 # 训练轮数
SHOW_EVERY = 3000 # 每次展示的轮数

FOOD_REWARD = 25 # 食物奖励
ENEMY_PENALTY = 300 # 遇敌惩罚
MOVE_PENALTY = 1 # 移动惩罚

epsilon = 0.6 # 随机概率
EPS_DECAY = 0.9998 # 随机概率下降
DISCOUNT = 0.95 # 学习折扣
LEARNING_RATE = 0.1 # 学习率

q_table = None #qtable文件名

# 颜色
d = {1:(255,0,0), #blue
     2:(0,255,0), #green
     3:(0,0,255)} #red

PLAYER_N = 1
FOOD_N = 2
ENEMY_N = 3


# %% [markdown]
# 建立类

# %%
# 建立类
class Cube:
    def __init__(self,name) -> None:
        self.name = name
        self.x = np.random.randint(0,SIZE)
        self.y = np.random.randint(0,SIZE)
        
    def __str__(self) -> str:
        return f'{self.name}\t({self.x},{self.y})'
    
    def __sub__(self,other):
        return (self.x-other.x,self.y-other.y)
    
    def action(self,choise):
        if choise == 0:
            self.move(x=1,y=1)
        elif choise == 1:
            self.move(x=1,y=-1)
        elif choise == 2:
            self.move(x=-1,y=1)
        elif choise == 3:
            self.move(x=-1,y=-1)
    
    def move(self,x=False,y=False):
        if not x:
            self.x += np.random.randint(-1,2)
        else:
            self.x += x
            
        if not y:
            self.y += np.random.randint(-1,2)
        else:
            self.y += y
            
        if self.x < 0:
            self.x = 0
        elif self.x >= SIZE:
            self.x = SIZE - 1
            
        if self.y < 0:
            self.y = 0
        elif self.y >= SIZE:
            self.y = SIZE - 1


# %% [markdown]
# 判断qtable是否存在，不存在就新建，存在则从文件拉取

# %%
if q_table is None:
    q_table = {}
    for x1 in range(-SIZE+1,SIZE):
        for y1 in range(-SIZE+1,SIZE):
            for x2 in range(-SIZE+1,SIZE):
                for y2 in range(-SIZE+1,SIZE):
                    q_table[((x1,y1),(x2,y2))] = [np.random.uniform(-5,0) for i in range(4)]
else:
    with open(q_table,'rb') as f:
        q_table = pickle.load(f)


# %% [markdown]
# 训练过程

# %%
episode_rewards = []
for episode in range(EPISODES):
    player = Cube('player')
    food = Cube('food')
    enemy = Cube('enemy')
    
    if episode%SHOW_EVERY == 0:
        print(f'episode #{episode},epsilon:{epsilon}')
        print(f'mean reward:{np.mean(episode_rewards[-SHOW_EVERY:])}')
        show = True
    else:
        show = False
        
        
    episode_reward = 0
    for i in range(200):
        obs = (player-food,player-enemy)
        if np.random.random() > epsilon:
            action = np.argmax(q_table[obs])
        else:
            action = np.random.randint(0,4)
        
        player.action(action)
        # food.move()
        # enemy.move()
        
        if player.x == food.x and player.y == food.y:
            reward = FOOD_REWARD
        elif player.x == enemy.x and player.y == enemy.y:
            reward = -ENEMY_PENALTY
        else:
            reward = -MOVE_PENALTY
        
        #Update the q_table
        current_q = q_table[obs][action]
        new_obs = (player-food,player-enemy)
        max_future_q = np.max(q_table[new_obs])
        
        if reward == FOOD_REWARD:
            new_q = FOOD_REWARD
        else:
            new_q = (1-LEARNING_RATE)*current_q+LEARNING_RATE*(reward+DISCOUNT*max_future_q)
        
        q_table[obs][action] = new_q
        

        '''绘制训练图像'''
        # if show:
        #     player = Cube('player')
        #     food = Cube('food')
        #     enemy = Cube('enemy')
        #     env = np.zeros((SIZE,SIZE,3),dtype=np.uint8)
        #     env[food.x][food.y] = d[FOOD_N]
        #     env[player.x][player.y] = d[PLAYER_N]
        #     env[enemy.x][enemy.y] = d[ENEMY_N]
        #     img = Image.fromarray(env,'RGB')
        #     img = img.resize((800,800))
        #     cv2.imshow('',np.array(img))
        #     if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:
        #         if cv2.waitKey(500) & 0xFF == ord('q'):
        #             break
        #     else:
        #         if cv2.waitKey(1) & 0xFF == ord('q'):
        #             break
        
        episode_reward += reward
        
        if reward == FOOD_REWARD or reward == -ENEMY_PENALTY:
            break
        
    episode_rewards.append(episode_reward)
    epsilon *= EPS_DECAY

# %% [markdown]
# 绘制训练结果图

# %%
# plot rewards
moving_avg = np.convolve(episode_rewards,np.ones((SHOW_EVERY,))/SHOW_EVERY,mode='valid')
print(len(moving_avg))
plt.plot([i for i in range(len(moving_avg))],moving_avg)
plt.xlabel('episode #')
plt.ylabel(f'mean {SHOW_EVERY} reward')
plt.figure().set_size_inches(6,8)
plt.show()

# %% [markdown]
# 保存qtable

# %%
# save qtable
with open(f'qtable_{int(time.time())}.pickle','wb') as f:
    pickle.dump(q_table,f)

# %%
# player = Cube('player')
# food = Cube('food')
# enemy = Cube('enemy')

# env = np.zeros((SIZE,SIZE,3),dtype=np.uint8)
# env[food.x][food.y] = d[FOOD_N]
# env[player.x][player.y] = d[PLAYER_N]
# env[enemy.x][enemy.y] = d[ENEMY_N]

# img = Image.fromarray(env,'RGB')
# img = img.resize((800,800))

# cv2.imshow('',np.array(img))

# if cv2.waitKey(500) & 0xFF == ord('q'):
#     pass


# %%
# moving_avg = np.convolve(episode_rewards,np.ones((SHOW_EVERY,))/SHOW_EVERY,mode='valid')
# print(len(moving_avg))
# plt.plot([i for i in range(len(moving_avg))],moving_avg)
# plt.xlabel('episode #')
# plt.ylabel(f'mean {SHOW_EVERY} reward')
# # plt.figure().set_size_inches(12,16)
# plt.figure(dpi=200)
# plt.show()


