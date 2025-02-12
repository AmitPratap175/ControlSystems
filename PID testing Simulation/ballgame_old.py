import pygame
import time
import numpy as np
import os
import yaml

# Used not to damage the camera from jerking too much close to the saturated value
with open('config.yaml','r') as file:
    data = yaml.safe_load(file)
    SAFELIMITS = data['SAFELIMITS']
    PANFACTOR, TILTFACTOR = data['pan_factor'], data['tilt_factor']

def create_folder(folder_path):
    # Check if the folder doesn't exist
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created.")
    else:
        print(f"Folder '{folder_path}' already exists.")

class BallGame:
    def __init__(self):
        # initialize pygame
        pygame.init()

        # define width of screen
        self.width = 1280
        # define height of screen
        self.height = 720
        self.screen_res = (self.width, self.height)

        pygame.display.set_caption("PID tracking of a Bouncing ball")
        self.screen = pygame.display.set_mode(self.screen_res)

        # define colors
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.green = (0,255,0)
        self.white = (255, 255, 255)

        # define ball
        self.ball_obj = pygame.draw.circle(
            surface=self.screen, color=self.red, center=[0, 0], radius=20)
        
        self.crosshair_size = 10
        #define cross hair
        self.cross_hair_obj = pygame.draw.line(self.screen, self.green, \
                                            (self.ball_obj.center[0],self.ball_obj.center[1] - self.crosshair_size),\
                                            (self.ball_obj.center[0],self.ball_obj.center[1] + self.crosshair_size), 2)

        # define speed of ball
        # speed = [X direction speed, Y direction speed]
        self.speed = [1, 1]

        # time difference
        self.dt = time.time()

        # game loop
        while True:
            self.main()
    
    def main(self):
        self.dt = time.time() - self.dt
        # event loop
        for event in pygame.event.get():
            # check if a user wants to exit the game or not
            if event.type == pygame.QUIT:
                exit()

        # fill black color on screen
        self.screen.fill(self.black)

        # move the ball
        # Let center of the ball is (100,100) and the speed is (1,1)
        self.ball_obj = self.ball_obj.move(self.speed)
        # Now center of the ball is (101,101)
        # In this way our wall will move

        # if ball goes out of screen then change direction of movement
        if self.ball_obj.left <= 0 or self.ball_obj.right >= self.width:
            self.speed[0] = -self.speed[0]
        if self.ball_obj.top <= 0 or self.ball_obj.bottom >= self.height:
            self.speed[1] = -self.speed[1]

        # draw ball at new centers that are obtained after moving ball_obj
        pygame.draw.circle(surface=self.screen, color=self.red,
                        center=self.ball_obj.center, radius=20)
        print(self.ball_obj.center , self.ball_obj.centerx, self.ball_obj.centery)
        # Draw the crosshair
        pygame.draw.line(self.screen, self.green, (self.ball_obj.center[0],self.ball_obj.center[1] - self.crosshair_size),\
                          (self.ball_obj.center[0],self.ball_obj.center[1] + self.crosshair_size), 2)
        pygame.draw.line(self.screen, self.green, (self.ball_obj.center[0]- self.crosshair_size,self.ball_obj.center[1]),\
                          (self.ball_obj.center[0] + self.crosshair_size,self.ball_obj.center[1]), 2)

        # update screen
        pygame.display.flip()

        self.dt = time.time()
        time.sleep(0.01)


BallGame()
