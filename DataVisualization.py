# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 22:45:42 2021

@author: 97jak
"""

import OvertimeAnalysis as oa
from matplotlib import pyplot as plt
import numpy as np

info = oa.get_drive_info('BAL',2019)

yards = []

for item in info:
    yards.append(item[2])

yards = np.array(yards)

plt.hist(yards,10)
plt.show()
