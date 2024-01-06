import pygame
from pygame.math import Vector2
import random 
import numpy as np

#initialize pygame library
pygame.init()



#set no of blocks should be there in screen to form grid
cell_size = 40
cell_number = 20

screen_size = cell_number * cell_size

#define screen area for displaying game
screen = pygame.display.set_mode((screen_size,screen_size))
screen.fill((175,215,70)) # screen background color 

#create timer to trigger change in display
screen_update = pygame.USEREVENT
pygame.time.set_timer(screen_update,10)

clock = pygame.time.Clock()

#font for displaying text on screen
font = pygame.font.Font('arial.ttf', 25)

# create a class for fruit 
class FRUIT:
    def __init__(self):
        self.randomize()

    def draw_fruit(self):
        fruit_rect = pygame.Rect(int(self.pos.x * cell_size),
                                 int(self.pos.y * cell_size),
                                 cell_size,
                                 cell_size)
        pygame.draw.rect(screen,(255,0,0),fruit_rect)
    
    def randomize(self):
        self.x = random.randint(0,cell_number-1)
        self.y = random.randint(0,cell_number-1)
        self.pos = Vector2(self.x,self.y)

#create a snake class
class SNAKE:
    def __init__(self):
        self.body = [Vector2(5,5),Vector2(4,5),Vector2(3,5)]
        self.direction = Vector2(1,0) 
        self.new_block = False
    def draw_snake(self):
        for block in self.body:
            x_pos = int(block.x * cell_size)
            y_pos = int(block.y * cell_size)
            block_rect = pygame.Rect(x_pos,
                                     y_pos,
                                     cell_size,
                                     cell_size)
            pygame.draw.rect(screen,(255,255,0),block_rect)
    def move_snake(self,action):
        clockwise = [Vector2(1,0),Vector2(0,1),Vector2(-1,0),Vector2(0,-1)]
        idx = clockwise.index(self.direction)
        if np.array_equal(action,[1,0,0]):
            new_direction = clockwise[idx]
        if np.array_equal(action,[0,1,0]):
            next_idx = (idx+1)%4
            new_direction = clockwise[next_idx]
        if np.array_equal(action,[0,0,1]):
            next_idx = (idx-1)%4
            new_direction = clockwise[next_idx]

        self.direction = new_direction

        if self.new_block:
            body_copy = self.body[:]
            body_copy.insert(0,body_copy[0]+self.direction)
            self.body = body_copy
            self.new_block = False
        else:
            body_copy = self.body[:-1]
            body_copy.insert(0,body_copy[0]+self.direction)
            self.body = body_copy

    def add_block(self):
        self.new_block = True

    def reset(self):
        self.body = [Vector2(5,10),Vector2(4,10),Vector2(3,10)]
        self.direction = Vector2(1,0) 

# create main class for handling all the logic
class MAIN:
    def __init__(self):
        self.snake = SNAKE()
        self.fruit = FRUIT()
        self.score = 0
        self.iteration = 0
        self.game_ended = False
        self.reward = 0
    def update(self,action):
        self.snake.move_snake(action)
        self.check_collision()
        self.check_fail()
        # pygame.display.update()
       

    def draw_elements(self):
        self.fruit.draw_fruit()
        self.snake.draw_snake()
        self.draw_score()

    def draw_score(self):
        text = font.render("Score: " + str(self.score), True, (255,255,255))
        screen.blit(text,(0,0))
    def check_collision(self):
        if self.fruit.pos == self.snake.body[0]:
            # print("collision")
            self.fruit.randomize()
            self.snake.add_block()
            self.score += 1
            self.reward += 10 

    def check_fail(self, pt = None)->bool:
        boolvalue = False
        
        if pt == None:
            pt = self.snake.body[0]

        if not (0 <= pt.x <= cell_number -1) or not (0 <= pt.y <= cell_number -1):
            boolvalue  = True
            
        for block in self.snake.body[1:]:
            if block == pt:
                boolvalue  = True
        return boolvalue
    
    def play(self,action):
        self.iteration += 1
        screen.fill((175,215,70))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                pygame.quit()
                quit()
            # move the snake 
            if event.type == screen_update:
                self.update(action)
            

        self.draw_elements()
        pygame.display.update()
        clock.tick(60)
        if (self.check_fail() == True) or (self.iteration > 100*len(self.snake.body)):
            self.game_ended = True
            self.reward += -10
            return self.reward, True, self.score
        else:
            return self.reward, False, self.score
        
        
    def game_over(self):
        self.score = 0
        self.snake.reset()
        self.iteration = 0
        self.fruit.randomize()

    

    
    
    
   