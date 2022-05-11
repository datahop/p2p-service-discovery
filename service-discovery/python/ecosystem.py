#!/usr/bin/python3
import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.ticker import StrMethodFormatter
from numpy import arange
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import zetac
from scipy.optimize import curve_fit


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def f(x, a):
    return (x**-a)/zetac(a)



def func_powerlaw(x, m, c, c0):
    return c0 + x**m * c

def zipf(x, a, c0):
    top = c0*(x**-a)
    bot  = zetac(a)
    print("top:", top, "| bot:", bot)
    return top/bot


a = 0.99999703
a=1.1
c0 = -2.0463e+09
n = 20000

#s = np.random.zipf(a, n)


lines = []
with open('./zipf_fitting/data.txt') as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

counts = []
for line in lines:
    count = int(line.split(':')[1])
    if count > 1:
        counts.append(count)


k = np.arange(1, 50)#len(counts))
print("k:", k)

counts = counts[::-1]
print("countS:", counts)

result = curve_fit(func_powerlaw, k, counts[0:len(k)], maxfev=10000)

print(result)


plt.bar(k, counts[0:len(k)], alpha=0.5, label='sample count')

plt.plot(k, func_powerlaw(k, *result), 'r-', label='fit: a=%5.3f, c0=%5.3f' % tuple(result))


#plt.plot(k, y, 'k.-', alpha=0.5,
#         label='expected count')   

plt.semilogy()

plt.grid(alpha=0.4)

plt.legend()

plt.title(f'Zipf sample, a={a}, size={n}')

plt.show()