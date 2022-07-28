#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import matplotlib

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# Define the expression whose roots we want to find
fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot()
n = 1000

for p_occupancy in [5, 10, 15]:
    for b in [0.0000001, 0.0001]:
        x_vals = []
        y_vals = []

        for x in range(1, 110000000, 10000):
            func = lambda d: x/(1+ b/(1-(d)/n)**p_occupancy) - (d)
            d = np.linspace(0, 300, 300)

            # Use the numerical solver to find the roots
            d_initial_guess = 10
            d_solution = fsolve(func, d_initial_guess)

            x_vals.append(x)
            y_vals.append(d_solution/n)
        if(b == 0.0001):
            ax.plot(x_vals, y_vals, label='p_occ=' + str(p_occupancy) + " b=" + str(b), linestyle = "--", linewidth = 2)
        elif (p_occupancy == 10):
            ax.plot(x_vals, y_vals, label='p_occ=' + str(p_occupancy) + " b=" + str(b), linestyle = "-", linewidth = 4)
        else:
            ax.plot(x_vals, y_vals, label='p_occ=' + str(p_occupancy) + " b=" + str(b), linestyle = "-", linewidth = 2)

plt.ylabel("d/n")
plt.xlabel("Request rate [bps]")

plt.axvline(x=10000000, color='red', linestyle='--')
plt.annotate("10Gbps", xy = (10000000*0.75, 0.7), horizontalalignment = 'center', color='red', rotation=90)

plt.axvline(x=1000000, color='red', linestyle='--')
plt.annotate("1Gbps", xy = (1000000*0.75, 0.75), horizontalalignment = 'center', color='red', rotation=90)

plt.axvline(x=1000, color='red', linestyle='--')
plt.annotate("1Mbps", xy = (1000*0.75, 0.75), horizontalalignment = 'center', color='red', rotation=90)

plt.xscale("log")
plt.ylim(0, 1)
#plt.legend()
plt.legend(loc='lower right')
plt.show()
