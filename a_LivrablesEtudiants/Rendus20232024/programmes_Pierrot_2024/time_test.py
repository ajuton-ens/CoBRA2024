
import time

start=time.time()

dicoTemps={0.01 : 0, 0.011:0, 0.012:0, 0.013:0, 0.014:0, 0.015:0, 0.016:0, 0.017:0, 0.018:0, 0.019:0, 0.02:0, 0.021:0, 0.022:0, 0.023:0, 0.024:0, 0.025:0, 0.026:0, 0.027:0,0.028:0,0.029:0,0.03:0}

n_iter=0

while True:
    if 0.01<(time.time()-start):
        dicoTemps[round(time.time()-start, 3)]+=1
        start=time.time()
        n_iter+=1
    if n_iter==1000:
        break