import sensors_lib.MyTFLuna as MyTFLuna

lidar = MyTFLuna.LidarTFLuna()


while True : 
    # PARTIE HAUTEUR 
    distanceh = lidar.read_distance()
    print(f"La distance mesurée par le télémètre infrarouge est: {distanceh}cm")   
        
