#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import matplotlib
from style import *

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}


matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

# Define the expression whose roots we want to find
ax, _ = plt.subplots()


n = 1000             # Table capacity
p_occupancy = 10
b = 0.0000001

N = 25000            # Network size
K_register = 5       # Number of registrations per bucket
N_A = 20             # Number of advertisers for topic A (will be overwritten in the for loop below)
N_B = 500           # Number of advertisers for topic B
N_A_B = 15000
R_X = 100            # Background number of registrations

x_vals = []
y_vals_A = []
y_vals_B = []
y_vals_A_B = []
y_vals_A_B_no_function = []

# The d equations for registrar close to topic A.
# This ignores the IP score, assuming that it is 0 ("worst case" of perfectly balanced addresses)
def equations_A(dvec):
    d_a = dvec[0]
    d_b = dvec[1]
    d_x = dvec[2]
    d = d_a + d_b + d_x
    t = 1 / (1 - d/n)**p_occupancy
    # Number of registrations that this registrar will get for topic A and B
    R_A = N_A
    R_B = K_register* N_B / (N/2)
    return [ R_A / (1+(b+d_a/d)*t) - d_a , R_B / (1+(b+d_b/d)*t) - d_b , R_X / (1+(b+d_x/d)*t) - d_x ]

def equations_B(dvec):
    d_a = dvec[0]
    d_b = dvec[1]
    d_x = dvec[2]
    d = d_a + d_b + d_x
    t = 1 / (1 - d/n)**p_occupancy
    # Number of registrations that this registrar will get for topic A and B
    R_A = K_register* N_A / (N/2)
    R_B = N_B
    return [ R_A / (1+(b+d_a/d)*t) - d_a , R_B / (1+(b+d_b/d)*t) - d_b , R_X / (1+(b+d_x/d)*t) - d_x ]

for a_to_b_ratio in range(1, 101):
    # Number of advertisers for topic A
    N_A = N_A_B / (1+a_to_b_ratio)
    N_B = N_A_B - N_A
    print("ratio:", a_to_b_ratio, "N_A:", N_A, "N_B:", N_B)
    #N_A = a_to_b_ratio * N_B


    x_vals.append(a_to_b_ratio)
    
    # This seems to be very sensitive to the initial guess!
    
    dvec_solutionA = fsolve(equations_A, [100,100,50])
    d_solutionA = dvec_solutionA[0]+dvec_solutionA[1]+dvec_solutionA[2]
    y_vals_A.append(d_solutionA/n)
    
    dvec_solutionB = fsolve(equations_B, [100,300,50])
    d_solutionB = dvec_solutionB[0]+dvec_solutionB[1]+dvec_solutionB[2]
    y_vals_B.append(d_solutionB/n)
    #print("A: ",N_A,dvec_solutionA, "   B: ",N_B,dvec_solutionB)

    y_vals_A_B.append(d_solutionB/d_solutionA)

    traffic_A =  N_A + (N_B * K_register) / (N/2) + R_X
    traffic_B =  N_B + (N_A * K_register) / (N/2) + R_X
    y_vals_A_B_no_function.append(traffic_B/traffic_A)
    
_, ax = plt.subplots()
#ax.plot(x_vals, y_vals_A, label="node A")
#ax.plot(x_vals, y_vals_B, label="node B")
ax.plot(x_vals, y_vals_A_B, label="with admission control", linewidth = 3, linestyle = "-")
index = x_vals.index(100)
y_value = y_vals_A_B[index]
formatted_y_value = "{:.1f}".format(y_value)
ax.annotate(f"{formatted_y_value}", xy=(100, y_value), xytext=(95, y_value + 10),
             arrowprops=dict(facecolor='black', arrowstyle='->'))
ax.plot(x_vals, y_vals_A_B_no_function, label="without admission control", linewidth = 3, linestyle = "--")

#plt.ylabel("RegistrarA / RegistrarB load ratio")
plt.ylabel(r'$\mathrm{r_A/r_B}$ load ratio')
plt.xlabel(r'$\mathrm{|A(s_A)|/|A(s_B)|}$')#, p_occupancy=" + str(p_occupancy) + ", b=" + str(b))

#plt.ylim(0, 1)
plt.legend()
plt.savefig('fairness_registration_new.pdf', bbox_inches='tight')
