#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File Name : test.py
Creation Date : mar. 06 mars 2018 17:27:32 CET
Last Modified : mer. 07 mars 2018 00:15:28 CET
Created By : Cyril Desjouy

Copyright © 2016-2018 Cyril Desjouy <ipselium@free.fr>
Distributed under terms of the BSD license.

-----------
DESCRIPTION

@author: Cyril Desjouy
"""

import matplotlib.pyplot as plt
import numpy as np

a = 1
b = 3

a = [i for i in range(11) if i % 2 == 0]
print(a)

for i in range(10):
    i = 3*i
    print(i)

x = np.linspace(0, 2*np.pi, 1000)

plt.figure()
plt.plot(x, np.cos(x))
plt.show()
