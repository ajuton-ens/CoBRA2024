#!/usr/bin/env python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 09:31:49 2024

@author: rdb
"""

import time
import fusion as lib
import statistics

c = lib.capteurs()

while True:
    vals = []
    for j in range(30):
        try:
            value = c.get()[0]
        except:
            vals.append(-1)
        else:
            vals.append(value)
        time.sleep(0.001)
    print(statistics.median(vals), vals)
