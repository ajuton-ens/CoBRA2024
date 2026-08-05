import cv2
import numpy as np
from dt_apriltags import Detector

try:
    # Initialize the AprilTag detector
    at_detector = Detector(families='tag36h11',
                           nthreads=1,
                           quad_decimate=1.0,
                           quad_sigma=0.0,
                           refine_edges=1,
                           decode_sharpening=0.25,
                           searchpath=['apriltags'])
    
    print("🚀 dt-apriltags is perfectly installed and initialized successfully!")
    
except Exception as e:
    print(f"❌ Initialization failed. Error: {e}")