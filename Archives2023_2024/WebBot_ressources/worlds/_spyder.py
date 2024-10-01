# -*- coding: utf-8 -*-
"""
Éditeur de Spyder

Ceci est un script temporaire.
"""
"""controller_test controller."""

# You may need to import some classes of the controller module. Ex:
#  from controller import Robot, Motor, DistanceSensor
import math
from controller import Robot, Motor, GPS

# create the Robot instance.
robot = Robot()

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

# You should insert a getDevice-like function in order to get the
# instance of a device of the robot. Something like:
k=300
erreur_angle = 2
objectif = [0, 0]
motor1 = robot.getDevice('helice_horizontale')
motor2 = robot.getDevice('helice_rotationelle')
gps = robot.getDevice('vittesse')
gps.enable(timestep)
capteur = robot.getDevice('capteur')
capteur.enable(timestep)
gyro = robot.getDevice('gyro')
gyro.enable(timestep)
#  ds = robot.getDevice('dsname')
#  ds.enable(timestep)
motor1.setPosition(float('inf'))
motor1.setVelocity(0)
motor2.setPosition(float('inf'))
motor2.setVelocity(0)
t = 0
temps = []
vittesses = []
position = gps.getValues()
vect = [position[0], position[2]]
vect_norme = [vect[0]/math.sqrt(position[0]**2 + position[1]**2), vect[1]/math.sqrt(position[0]**2 + position[1]**2)]            
L_vect = [vect_norme]
angles = [0, 0, 0]
er_a = float('inf')
# - perform simulation steps until Webots is stopping the controller
while robot.step(timestep) != -1 and er_a > erreur_angle :
    # Read the sensors:
    # Enter here functions to read sensor data, like:
    #  val = ds.getValue()
    position = gps.getValues()
    for i in range(3):
        angles[i] = angles[i] + gyro.getValues()[i]*timestep*0.001
    vect = [objectif[0]-position[0], objectif[1]-position[1]]
    vect_norme = [vect[0]/math.sqrt(vect[0]**2 + vect[1]**2), vect[1]/math.sqrt(vect[0]**2 + vect[1]**2)]
    if math.acos(vect_norme[0])>0:
        if math.asin(vect_norme[1])>0:
            angle_i = math.acos(vect_norme[0])*
        else :
            angle_i = - math.acos(vect_norme[0]) 
    else : 
        if math.asin(vect_norme[1])>0:
            angle_i = math.acos(vect_norme[0])
        else :
            angle_i = - math.acos(vect_norme[0])
while robot.step(timestep) != -1 :
    
    if position[0] == 0 and position[2] == 0 :
            motor1.setVelocity(0)
            motor2.setVelocity(0)
    # Process sensor data here.
    print('angles = ', angles)
    # Enter here functions to send actuator commands, like:
    #  motor.setPosition(10.0)
    pass
 