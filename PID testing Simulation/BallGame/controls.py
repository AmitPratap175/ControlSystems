import os
import yaml
import numpy as np
import time

# Used not to damage the camera from jerking too much close to the saturated value


def create_folder(folder_path):
    # Check if the folder doesn't exist
    if not os.path.exists(folder_path):
        # Create the folder
        os.makedirs(folder_path)

class GimbalControl:
    def __init__(self,offset,version = 1):  
        with open('config.yaml','r') as file:
            self.data = yaml.safe_load(file)
                
        self.W = 1280
        self.H = 720
        self.flipper = True
        self.offset = offset
        self.pan, self.tilt = 0, 0

        self.pan_factor, self.tilt_factor = self.data['pan_factor'], self.data['tilt_factor']

        # PID object pan and tilt
        self.PID_x = PID(self.data)
        self.PID_x.initialize() 
        self.PID_y = PID(self.data)
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
    
    def update(self,dt,offset,speed_ball):
        # Control Gimbal -----------------
        self.offset = offset
        self.inv_speed_conversion(speed_ball)
        # mavlink controller           
        # if self.flipper:
        if self.offset[0] > 1/64:
            offs = 1
            self.pan = 1500 + int(400 * (self.pan_factor) * offs)

            #PID 
            self.pan_PID = 1500 + int(self.PID_x.update(dt, self.offset[0] - 1/64, self.ref_speed_pan))
        elif self.offset[0] < -1/64:
            offs = -1
            self.pan = 1500 + int(400 * (self.pan_factor) * offs)

            #PID
            self.pan_PID = 1500 + int(self.PID_x.update(dt, self.offset[0] + 1/64, self.ref_speed_pan))
        else:
            self.pan = 1500
            self.pan_PID = 1500
        
        # print(colored("PWM-->", 'green'), colored("Pan:", 'yellow'), "{:d}".format(self.pan))
        #self.gimbal_control.set_rc_channel_pwm(int(self.config['pan_channel']), self.pan)
        
        # self.flipper = False
        
        # else:
        if self.offset[1] > 1/64:
            offs = 1
            self.tilt = 1500 + int(400 * (self.tilt_factor) * offs)
            
            #PID 
            self.tilt_PID = 1500 + int(self.PID_y.update(dt, self.offset[1] - 1/64, self.ref_speed_tilt))
            
        elif self.offset[1] < -1/64:
            offs = -1
            self.tilt = 1500 + int(400 * (self.tilt_factor) * offs)

            #PID 
            self.tilt_PID = 1500 + int(self.PID_y.update(dt, self.offset[1] + 1/64, self.ref_speed_tilt))
        # print(colored("PWM-->", 'green'), colored('Tilt:', 'yellow'), "{:d}\n".format(self.tilt))
        else:
            offs = 0
            self.tilt = 1500
            #PID 
            self.tilt_PID = 1500 

        #write to the file for comparision
        self.write()    

        # print(f"OFFSET: {self.offset[0]}  {self.offset[1]}  PAN: {self.pan}  {self.pan_PID}  TILT: {self.tilt}  {self.tilt_PID}\n")

        return self.speed_conversion()

    def write(self):
        with open(self.filename,'a+') as file1:
            file1.write(f"{self.offset[0]}  {self.offset[1]}  {self.pan}  {self.pan_PID}  {self.tilt}  {self.tilt_PID}\n")

    def speed_conversion(self):
        return np.ceil((self.pan - 1500) / self.data['SPEEDCONVERSION']), np.ceil((self.tilt - 1500) / self.data['SPEEDCONVERSION']),\
              np.ceil((self.pan_PID - 1500) / self.data['SPEEDCONVERSION']), np.ceil((self.tilt_PID - 1500) / self.data['SPEEDCONVERSION'])

    def inv_speed_conversion(self,speed_ball):
        self.ref_speed_pan =  self.data['SPEEDCONVERSION'] * speed_ball[0] + 1500
        self.ref_speed_tilt = self.data['SPEEDCONVERSION'] * speed_ball[1] + 1500
    
class PID:
    """
    The following is the code to generate the PID PWM values for the appropriate offsets. We have to define two PID loops,
    each for the two offset corrections in pan and tilt and record the values in a file for the examination.

    The file format is {offset_x} {offset_y} {pan} {pan_PID} {tilt} {tilt_PID}.
    """
    def __init__(self,data):
        # initialize gains
        self.kP = data['Kp']
        self.kI = data['Ki']
        self.kD = data['Kd']
        self.LS = RLS(3)
        self.MaxOutput = 400  
        self.MinOutput = 0
        self.sign = 0  
        self.SafeLimits = data['SAFELIMITS']


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
        

    def update(self, dt ,offset, ref_speed):
        
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
        # pid = self.kP * self.P + self.kI * self.I + self.kD * self.D
        pid=np.array([self.P, self.I , self.D])
        
        pid_out =  np.clip(float(pid * self.LS.w), self.MinOutput, self.MaxOutput)
        # print(float(pid * self.LS.w))
        # self.LS.w.flatten()
        # k = self.LS.w
        # print(k)
        print(float(self.LS.w[0][0]), float(self.LS.w[1][0]),\
                                     float(self.LS.w[2][0]))

        self.kP, self.kI, self.kD =  float(self.LS.w[0][0]), float(self.LS.w[1][0]),\
                                     float(self.LS.w[2][0])
        self.LS.add_obs(pid.T, ref_speed)

        return pid_out
    

class RLS:
    def __init__(self, num_vars = 3, lam = 0.85, delta = 1):
        '''
        num_vars: number of variables including constant
        lam: forgetting factor, usually very close to 1.
        '''
        self.num_vars = num_vars
        
        # delta controls the initial state.
        self.A = delta*np.matrix(np.identity(self.num_vars))
        self.w = np.matrix(np.zeros(self.num_vars))
        self.w = self.w.reshape(self.w.shape[1],1)
        
        # Variables needed for add_obs
        self.lam_inv = lam**(-1)
        self.sqrt_lam_inv = np.sqrt(self.lam_inv)
        
        # A priori error
        self.a_priori_error = 0
        
        # Count of number of observations added
        self.num_obs = 0

    def add_obs(self, x, t):
        '''
        Add the observation x with label t.
        x is a column vector as a numpy matrix
        t is a real scalar
        '''            
        z = self.lam_inv*self.A*x
        alpha = float((1 + x.T*z)**(-1))
        self.a_priori_error = float(t - self.w.T*x)
        self.w = self.w + (t-alpha*float(x.T*(self.w+t*z)))*z
        self.A -= alpha*z*z.T
        self.num_obs += 1
        
    # def fit(self, X, y):
    #     '''
    #     Fit a model to X,y.
    #     X and y are numpy arrays.
    #     Individual observations in X should have a prepended 1 for constant coefficient.
    #     '''
    #     for i in range(len(X)):
    #         x = np.transpose(np.matrix(X[i]))
    #         self.add_obs(x,y[i])


    # def get_error(self):
    #     '''
    #     Finds the a priori (instantaneous) error. 
    #     Does not calculate the cumulative effect
    #     of round-off errors.
    #     '''
    #     return self.a_priori_error
    
    # def predict(self, x):
    #     '''
    #     Predict the value of observation x. x should be a numpy matrix (col vector)
    #     '''
    #     return float(self.w.T*x)