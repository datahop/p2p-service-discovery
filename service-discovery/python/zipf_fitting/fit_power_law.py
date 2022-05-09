import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import zetac
import numpy.random as random
from scipy.stats import zipf


def zipf1(x, a, c0):
    return c0*(x**-a)/zetac(a)

def funct(x, alpha, x0):
    return((x+x0)**(-alpha))

def func_powerlaw(x, m, c, c0):
    return c0 + x**m * c

lines = []
with open('data.txt') as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

counts = []
for line in lines:
    count = int(line.split(':')[1])
    if count > 7:
        counts.append(count)
    #counts.append(int(line.split(':')[1]))

counts.reverse()
topics = list(range(1, len(counts)+1))

df = pd.DataFrame({
            'x': topics,
            'y': counts
        })
df.plot(x='x', y='y', kind='line', style='--ro', figsize=(10, 5))


target_func = zipf1

X = df['x']
y = df['y']

popt, pcov = curve_fit(target_func, X, y, maxfev=10000)

print('popt: ', popt, ' pcov: ', pcov)

plt.figure(figsize=(10, 5))
plt.plot(X, target_func(X, *popt), '--')
plt.plot(X, y, 'ro')
plt.legend()
plt.show()
