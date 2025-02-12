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

        # gimball 
        gimbal = GimbalControl((40,0))

        # define ball
        self.ball_obj = pygame.draw.circle(
            surface=self.screen, color=self.red, center=[self.width // 2 + 100, self.height // 2 + 100], radius=20)
        
        # define cross hair
        self.crosshair_size = 10
        self.cross_hair_x1 = (self.width // 2,self.height // 2 - self.crosshair_size)
        self.cross_hair_x2 = (self.width // 2,self.height // 2 + self.crosshair_size)

        self.cross_hair_y1 = (self.width // 2 - self.crosshair_size, self.height // 2)
        self.cross_hair_y2 = (self.width // 2 + self.crosshair_size, self.height // 2)

        self.cross_hair_obj_x = pygame.draw.line(self.screen, self.green, \
                                            self.cross_hair_x1,\
                                            self.cross_hair_x2, 2)
        self.cross_hair_obj_y = pygame.draw.line(self.screen, self.green, \
                                            self.cross_hair_y1,\
                                            self.cross_hair_y2, 2)

        # define speed of ball
        # speed = [X direction speed, Y direction speed]
        self.ball_speed = [1, 20]
        self.crosshair_speed = [5, 5]

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

        # follow the movement of the ball
        if np.abs(self.cross_hair_obj_x.centerx - self.ball_obj.centerx) > 10:
            delta = self.cross_hair_obj_x.centerx - self.ball_obj.centerx
            self.crosshair_speed[0] = int(np.clip(np.abs(delta),0,2) * -np.sign(delta) * self.ball_speed[0])
        elif np.abs(self.cross_hair_obj_x.centerx - self.ball_obj.centerx) < 10:
            self.crosshair_speed[0] = self.ball_speed[0]
        if self.cross_hair_obj_x.centerx - self.crosshair_size <= 0 or self.cross_hair_obj_x.centerx + self.crosshair_size >= self.width:
            self.crosshair_speed[0] = -self.crosshair_speed[0]
        if np.abs(self.cross_hair_obj_y.centery - self.ball_obj.centery) > 10:
            delta = self.cross_hair_obj_y.centery - self.ball_obj.centery
            self.crosshair_speed[1] = int(np.clip(np.abs(delta),0,2) * -np.sign(delta) * self.ball_speed[1])
        elif np.abs(self.cross_hair_obj_y.centery - self.ball_obj.centery) < 10:
            self.crosshair_speed[1] = self.ball_speed[1]
        if self.cross_hair_obj_y.centery - self.crosshair_size <= 0 or self.cross_hair_obj_y.centery + self.crosshair_size >= self.height:
            self.crosshair_speed[1] = -self.crosshair_speed[1]

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

class GimbalControl:
    def __init__(self,offset,version = 1):        
        self.W = 1280
        self.H = 720
        self.flipper = True
        self.offset = offset
        self.pan, self.tilt = 0, 0

        self.pan_factor, self.tilt_factor = PANFACTOR, TILTFACTOR

        # PID object pan and tilt
        self.PID_x = PID()
        self.PID_x.initialize() 
        self.PID_y = PID()
        self.PID_y.initialize()
        self.pan_PID, self.tilt_PID = 0, 0
        self.flag = False
        
        while not self.flag:
            create_folder(f'./PAN_TILT_{self.pan_factor}/')

            if f'PIDvsLinearControl_{version}.txt' not in os.listdir(f'./PAN_TILT_{self.pan_factor}/'):
                self.flag = True
                #file to save the values for comparision
                self.filename = f'./PAN_TILT_{self.pan_factor}/PIDvsLinearControl_{version}.txt'
            else:
                version += 1
                print("version: ",version)
    
    def update(self,dt):
        # Control Gimbal -----------------
        
        # mavlink controller           
        # if self.flipper:
        if self.offset[0] > 0.1:
            offs = 1
            self.pan = 1500 + int(400 * (self.pan_factor) * offs)

            #PID 
            self.pan_PID = 1500 + int(self.PID_x.update(dt, self.offset[0] - 0.1))
        elif self.offset[0] < -0.1:
            offs = -1
            self.pan = 1500 + int(400 * (self.pan_factor) * offs)

            #PID
            self.pan_PID = 1500 + int(self.PID_x.update(dt, self.offset[0] + 0.1))
        else:
            self.pan = 1500
            self.pan_PID = 1500
        
        # print(colored("PWM-->", 'green'), colored("Pan:", 'yellow'), "{:d}".format(self.pan))
        #self.gimbal_control.set_rc_channel_pwm(int(self.config['pan_channel']), self.pan)
        
        # self.flipper = False
        
        # else:
        if self.offset[1] > 0.1:
            offs = 1
            self.tilt = 1500 + int(400 * (self.tilt_factor) * offs)
            
            #PID 
            self.tilt_PID = 1500 + int(self.PID_y.update(dt, self.offset[1] - 0.1))
            
        elif self.offset[1] < -0.1:
            offs = -1
            self.tilt = 1500 + int(400 * (self.tilt_factor) * offs)

            #PID 
            self.tilt_PID = 1500 + int(self.PID_y.update(dt, self.offset[1] + 0.1))
        # print(colored("PWM-->", 'green'), colored('Tilt:', 'yellow'), "{:d}\n".format(self.tilt))
        else:
            offs = 0
            self.tilt = 1500
            #PID 
            self.tilt_PID = 1500 

        #write to the file for comparision
        self.write()    

        print(f"OFFSET: {self.offset[0]}  {self.offset[1]}  PAN: {self.pan}  {self.pan_PID}  TILT: {self.tilt}  {self.tilt_PID}\n")

    def write(self):
        with open(self.filename,'a+') as file1:
            file1.write(f"{self.offset[0]}  {self.offset[1]}  {self.pan}  {self.pan_PID}  {self.tilt}  {self.tilt_PID}\n")
    
class PID:
    """
    The following is the code to generate the PID PWM values for the appropriate offsets. We have to define two PID loops,
    each for the two offset corrections in pan and tilt and record the values in a file for the examination.

    The file format is {offset_x} {offset_y} {pan} {pan_PID} {tilt} {tilt_PID}.
    """
    def __init__(self, kP=100, kI=200, kD=15):
        # initialize gains
        self.kP = kP
        self.kI = kI
        self.kD = kD
        self.MaxOutput = 400  
        self.MinOutput = 0
        self.sign = 0  
        self.SafeLimits = SAFELIMITS


    def initialize(self):

        # initialize the previous offset
        self.prevOffset = 0

        # initialize the term result variables
        self.P = 0
        self.I = 0
        self.D = 0

    def limits(self):
        if self.sign == 1:
            self.MaxOutput = 400 * self.SafeLimits
            self.MinOutput = 0
        else:
            self.MaxOutput = 0  
            self.MinOutput = -400 * self.SafeLimits
        

    def update(self, dt ,offset):
        
        deltaTime = dt
        # update the sign
        self.sign = np.sign(offset)

        # update the limits according to the sign of the offset 
        self.limits()

        # use the current time to calculate delta time
        self.currTime = time.time()

        # delta offset
        deltaOffset = offset - self.prevOffset

        # proportional term
        self.P = offset

        # integral term
        self.I += offset * deltaTime

        # derivative term and prevent divide by zero
        self.D = (deltaOffset / deltaTime) 

        # save previous time and offset for the next update
        self.prevTime = self.currTime
        self.prevOffset = offset
        pid = self.kP * self.P + self.kI * self.I + self.kD * self.D

        pid_out =  np.clip(pid, self.MinOutput, self.MaxOutput)

        return pid_out

BallGame()
