import time
from datetime import datetime

f =open("/home/ajuton/Documents/a0_Saphire/Dirigeable/asservissement/dates.txt", "w")
start = time.time()
while time.time() - start < 1.0:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    f.write(now + "\n")
    f.flush()
    time.sleep(0.01)