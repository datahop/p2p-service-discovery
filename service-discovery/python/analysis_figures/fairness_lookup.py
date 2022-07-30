import scipy.special
import random
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import matplotlib


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 16}


matplotlib.rc('font', **font)
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42

n = 1000             # Table capacity
p_occupancy = 10
b = 0.0000001

N = 25000
K_register = 4
N_return = 10        # Maximum number of results returned by a registrar
L_lookup = 4         # Number of lookups per bucket
N_A = 1000
R_B = 100
R_X = 500            # Background number of registrations

num_runs = 100000    # Number of simulation runs

def number_unique(num_lookups):
    num_advertisers = N_A
    #num_unique = 0
    #for i in range(0,N_return):
        # https://stats.stackexchange.com/questions/296005/the-expected-number-of-unique-elements-drawn-with-replacement
        #num_unique += num_advertisers * (1 - ( (num_advertisers-1)/num_advertisers ) ** num_lookups)
        #num_advertisers -= 1
    num_unique = num_advertisers * (1 - ( (num_advertisers-1)/num_advertisers ) ** (num_lookups*N_return))
    return num_unique
    

# Gives the probability that a registrar will be chosen by an advertiser in bucket "bucket"
def p_reg_single(bucket):
    return max(1,min(K_register, N/2**bucket)) / max(1,N/2**bucket)

# probability that a registrar will be chosen by exactly "r" advertisers (out of "advertisers" advertisers) in bucket "bucket"
def p_reg(advertisers, r, bucket):
    return scipy.special.binom(advertisers,r) * p_reg_single(bucket)**r * (1-p_reg_single(bucket))**(advertisers-r)

# The d equations for registrar close to topic A.
# This ignores the IP score, assuming that it is 0 ("worst case" of perfectly balanced addresses)
def equations_A(dvec, R_A):
    d_a = dvec[0]
    d_b = dvec[1]
    d_x = dvec[2]
    d = d_a + d_b + d_x
    t = 1 / (1 - d/n)**p_occupancy
    return [ R_A / (1+(b+d_a/d)*t) - d_a , R_B / (1+(b+d_b/d)*t) - d_b , R_X / (1+(b+d_x/d)*t) - d_x ]

# Calculates the distribution of the number of ads that a registrar in bucket "bucket"
# will return, assuming "N_A" advertisers for that topic.
# The result is an array where entry i is the probability that [i,i+1[ ads are returned.
def response_distr_node(bucket):
    num_lookups = max(1,min(L_lookup, N/2**bucket))
    unique_factor = number_unique(num_lookups) / (num_lookups*N_return)
    distr = [0] * (N_return+1)
    for r in range(0,N_A+1):
        prob = p_reg(N_A, r, bucket)
        if prob>0:
            dvec = fsolve(equations_A, [100,200,50], args=[ r ])
            ads = dvec[0]
            if ads>N_return:     # Truncate the number of ads returned
                ads = N_return
            distr[int(ads* unique_factor)] += prob
    return distr

# Samples a random value from a discrete distribution ("distr" is a histogram)
def sample_distr(distr):
    rnd = random.uniform(0, 1)
    i = 0
    while rnd>=0 and i<len(distr):
        rnd -= distr[i]
        i += 1
    return i-1

def response_distr_bucket(bucket):    
    distr = [0] * (N_return*L_lookup+1)
    distr_node = response_distr_node(bucket)
    for i in range(0,10000):
        ads = 0
        for j in range(0,L_lookup):
            ads += sample_distr(distr_node) 
        distr[ads] += 1
    for i in range(0,len(distr)):
        distr[i] /= 10000
    return distr

def response_distr(num_buckets):
    distr = [0] * (N_return*L_lookup*num_buckets+1) 
    distr_node = [0]*num_buckets
    for i in range(0,num_buckets):
       distr_node[i] = response_distr_node(i+1)
    for i in range(0,num_runs):
        ads = 0
        for k in range(0,num_buckets):
            num_lookups = int(max(1,min(L_lookup, N/2**k)))
            for j in range(0,num_lookups):
                ads += sample_distr(distr_node[k])
        distr[ads] += 1    
    for i in range(0,len(distr)):
        distr[i] /= num_runs
    return distr
        
num_buckets = 8

fig = plt.figure(figsize=(10, 4))
ax = fig.add_subplot()


max_i = 452
step = 10

for K in [3, 5, 7]:
    x_vals = []
    y_vals = []
    K_lookup = K
    K_register = K
    for i in range(1, max_i, step):
        N_A = i
        distr = response_distr(num_buckets)
    #ax.plot([*range(0,len(distr))], distr, label="number of ads received for topic A after "+str(num_buckets)+" buckets", linewidth = 3, linestyle = "-")

    # calculate probability to have less than 30 responses:
        p30 = 0
        for i in range(0,30):
            p30 += distr[i]
        print("Probability to have less than 30 responses after "+str(num_buckets)+" = "+str(p30)) 
        print("The load on the last node is", p30 * N_A)

        x_vals.append(N_A)
        y_vals.append(p30 * N_A)


    ax.plot(x_vals, y_vals, label="K_lookup/K_register=" + str(K))

plt.ylabel("Lookup load on registrar A")
plt.xlabel("N_a")
plt.legend()
plt.show()
