import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import zetac
import numpy.random as random
from scipy.stats import zipf
import matplotlib

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}

matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42


def f (x, a, b, c):
    return 1/(x) + c

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
    #if count > 7:
    counts.append(count)
    #counts.append(int(line.split(':')[1]))

labels = ['mainnet', 'ropsten', 'rinkeby', 'goerly', 'binance', '', '', '', 'musicoin', '', '', '', 'pirl']

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

popt, pcov = curve_fit(target_func, X, y, maxfev=1000000)

print('popt: ', popt, ' pcov: ', pcov)

#fig, ax = 
plt.figure(figsize=(10, 4))
plt.plot(X, target_func(X, *popt), '--', color='black', label = 'Zipf distribution')
plt.plot(X, y, 'ro', color='tab:blue', label = 'Ethereum sub-networks')
plt.legend()
plt.ylabel('#Nodes')
plt.xlabel('Rank')
plt.semilogy()
for i in range(0, len(labels)):
    x_pos = X[i] + 5
    y_pos = y[i]
    if(labels[i] == 'rinkeby'):
        y_pos -= 150
    if(labels[i] == 'goerly'):
        y_pos -= 400
    plt.annotate(labels[i] , xy = (x_pos, y_pos), horizontalalignment = 'left', color='black')
plt.show()
