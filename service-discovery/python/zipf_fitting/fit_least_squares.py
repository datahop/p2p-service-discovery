import numpy as np
from scipy.special import zetac
import matplotlib.pyplot as plt
from lmfit import Model

def test(x, a, b, c): 
    return (a + b*np.log(x) + c*np.log(x)**2)

def func_powerlaw(x, m, c, c0):
    return c0 + x**m * c

def zipf(x, a, c0):
    return c0*(x**-a)/zetac(a)

def funct(x, alpha, x0):
    return((x+x0)**(-alpha))

lines = []
with open('data.txt') as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]

counts = []
for line in lines:
    count = int(line.split(':')[1])
    if count > 1:
        counts.append(count)

counts.reverse()
topics = list(range(1, len(counts)+1))
print('Number of topics: ', len(topics))


# create model from your model function
#mymodel = Model(func_powerlaw)
#mymodel = Model(zipf)
mymodel = Model(zipf)
#mymodel = Model(zipf)

# create initial set of named parameters from argument of your function

#params = mymodel.make_params(m=0.5, c0=2, c=1)
params = mymodel.make_params(c0=10, a=0.7)
#params = mymodel.make_params(x0=0.1, alpha=0.7)
#params = mymodel.make_params(a=0.7)

# Create some dummy data
x_data = topics
y_data = counts #   np.log(x_data) + np.log(x_data)**2 + np.random.random(len(x_data))

# run fit, get result
result = mymodel.fit(y_data, params, x=x_data)

# print out full fit report: fit statistics, best-fit values, uncertainties
print(result.fit_report())

# make a stacked plot of residual and data + fit
result.plot()
#plt.semilogy()
plt.show()
