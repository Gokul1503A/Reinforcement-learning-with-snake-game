import torch
import random
import numpy as np
from RL_game import MAIN
from collections import deque
from pygame.math import Vector2
from model import Linear_QNet, QTrainer
from helper import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001

class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 #randomness
        self.gamma = 0.9 # discount rate between 0 and 1
        self.memory = deque(maxlen = MAX_MEMORY) # when memory is full removes left 
        #model,train
        self.model = Linear_QNet(11,256,3)
        self.trainer = QTrainer(self.model,LR,self.gamma)

    def get_state(self,game):

        head = game.snake.body[0]
        point_l = Vector2(head.x - 40, head.y)
        point_r = Vector2(head.x + 40, head.y)
        point_u = Vector2(head.x, head.y - 40)
        point_d = Vector2(head.x, head.y + 40)
        
        dir_l = game.snake.direction == Vector2(-1,0)
        dir_r = game.snake.direction == Vector2(1,0)
        dir_u = game.snake.direction == Vector2(0,-1)
        dir_d = game.snake.direction == Vector2(0,1)

        state = [
            # Danger straight
            (dir_r and game.check_fail(point_r)) or 
            (dir_l and game.check_fail(point_l)) or 
            (dir_u and game.check_fail(point_u)) or 
            (dir_d and game.check_fail(point_d)),

            # Danger right
            (dir_u and game.check_fail(point_r)) or 
            (dir_d and game.check_fail(point_l)) or 
            (dir_l and game.check_fail(point_u)) or 
            (dir_r and game.check_fail(point_d)),

            # Danger left
            (dir_d and game.check_fail(point_r)) or 
            (dir_u and game.check_fail(point_l)) or 
            (dir_r and game.check_fail(point_u)) or 
            (dir_l and game.check_fail(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.fruit.pos.x < head.x,  # food left
            game.fruit.pos.x > head.x,  # food right
            game.fruit.pos.y < head.y,  # food up
            game.fruit.pos.y > head.y  # food down
            ]
        
        return np.array(state, dtype=int)
    
    def remember(self,state,action,reward,next_state,done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached
    
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)

    def train_short_memory(self,state,action,reward,next_state,done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self,state):
        # first we go with random moves to understand about evironment
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0,200)<self.epsilon:
            move = random.randint(0,2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state,dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = MAIN()

    while True:
        #get old state
        state_old = agent.get_state(game)

        #get move
        final_move = agent.get_action(state_old)

        #perform move and new state 

        reward,done,score = game.play(final_move)

        state_new = agent.get_state(game)

        #train short memory

        agent.train_short_memory(state_old,final_move,reward,state_new,done)

        # remember 
        agent.remember(state_old,final_move,reward,state_new,done)

        if done:
            #train long memory , plot result
            game.game_over()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agnent.model.save
            
            print(f"game{agent.n_games}, score {score}, record {record}")
            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

train()