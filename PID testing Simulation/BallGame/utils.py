import pygame
import time
import numpy as np

from controls import GimbalControl
        

class BallGame:
    def __init__(self):
        # initialize pygame
        pygame.init()

        # define width of screen
        self.width = 1280
        self.scalefactor_x = self.width // 2
        # define height of screen
        self.height = 720
        self.scale_factor_y = self.height // 2
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
            surface=self.screen, color=self.red, center=[self.width // 2 + 100, self.height // 2 + 100], radius=20)
        
        # define cross hair
        self.crosshair_size = 10
        self.cross_hair_x1 = (self.width // 2 - 100,self.height // 2 - self.crosshair_size)
        self.cross_hair_x2 = (self.width // 2 - 100,self.height // 2 + self.crosshair_size)

        self.cross_hair_y1 = (self.width // 2 - self.crosshair_size - 100, self.height // 2)
        self.cross_hair_y2 = (self.width // 2 + self.crosshair_size -100, self.height // 2)

        self.cross_hair_obj_x = pygame.draw.line(self.screen, self.green, \
                                            self.cross_hair_x1,\
                                            self.cross_hair_x2, 2)
        self.cross_hair_obj_y = pygame.draw.line(self.screen, self.green, \
                                            self.cross_hair_y1,\
                                            self.cross_hair_y2, 2)

        # define speed of ball
        # speed = [X direction speed, Y direction speed]
        self.ball_speed = [1, 2]
        self.crosshair_speed = [5, 5]
        self.speed_stack_x = []
        self.speed_stack_y = []

        # gimball 
        self.gimbal = GimbalControl((-(self.cross_hair_obj_x.centerx - self.ball_obj.centerx) / self.scalefactor_x,\
                                     -(self.cross_hair_obj_y.centery - self.ball_obj.centery) / self.scale_factor_y))

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
        self.ball_obj = self.ball_obj.move(self.ball_speed)
        # Now center of the ball is (101,101)
        # In this way our wall will move

        # if ball goes out of screen then change direction of movement
        if self.ball_obj.left <= 0 or self.ball_obj.right >= self.width:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_obj.top <= 0 or self.ball_obj.bottom >= self.height:
            self.ball_speed[1] = -self.ball_speed[1]

        # draw ball at new centers that are obtained after moving ball_obj
        pygame.draw.circle(surface=self.screen, color=self.red,
                        center=self.ball_obj.center, radius=20)

        # follow the movement of the ball by changing the 
        delta_x = -(self.cross_hair_obj_x.centerx - self.ball_obj.centerx) / self.scalefactor_x
        delta_y = -(self.cross_hair_obj_y.centery - self.ball_obj.centery) / self.scale_factor_y

        _,_,speed_x,speed_y =self.gimbal.update(self.dt, (delta_x,delta_y), self.ball_speed)
        
        if len(self.speed_stack_x)==3:
            self.speed_stack_x[0:2], self.speed_stack_y[0:2] = self.speed_stack_x[1:], self.speed_stack_y[1:]
            self.speed_stack_x[2], self.speed_stack_y[2] = speed_x,speed_y
            self.crosshair_speed[0],self.crosshair_speed[1] = self.speed_stack_x[0], self.speed_stack_y[0]
        else:
            self.speed_stack_x.append(speed_x)
            self.speed_stack_y.append(speed_y)
            self.crosshair_speed[0],self.crosshair_speed[1] = 0, 0

        self.cross_hair_obj_x = self.cross_hair_obj_x.move(self.crosshair_speed)
        self.cross_hair_obj_y = self.cross_hair_obj_y.move(self.crosshair_speed)
        # Draw the crosshair
        pygame.draw.line(self.screen, self.green, (self.cross_hair_obj_x.centerx,self.cross_hair_obj_x.centery - self.crosshair_size),\
                                                  (self.cross_hair_obj_x.centerx,self.cross_hair_obj_x.centery + self.crosshair_size), 2)
        pygame.draw.line(self.screen, self.green, (self.cross_hair_obj_y.centerx - self.crosshair_size, self.cross_hair_obj_y.centery),\
                                                  (self.cross_hair_obj_y.centerx + self.crosshair_size, self.cross_hair_obj_y.centery), 2)

        # update screen
        pygame.display.flip()

        self.dt = time.time()
        time.sleep(0.01)



