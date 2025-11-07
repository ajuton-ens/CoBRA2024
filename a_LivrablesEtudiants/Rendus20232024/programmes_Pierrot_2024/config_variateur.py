import time
from adafruit_servokit import ServoKit
import math

kit = ServoKit(channels=16)
t0 = time.time()
while time.time() - t0 < 10:
    th = math.sin(2*math.pi*time.time()/2.5)
    kit.continuous_servo[1].throttle = th
    print(th)
    time.sleep(0.1)

kit.continuous_servo[1].trottle = 0