import simpy
from table import *
import matplotlib.pyplot as plt
from threshold import *


run_time = 100000
ad_lifetime = 300
capacity = 200

env = simpy.Environment()
table = SimpleTable(env, capacity, ad_lifetime)
#table = DiversityThreshold(env, capacity, ad_lifetime, topicThresholds = {"t1" : 0.5, "t2" : 0.5},  ipThresholds = {8: capacity/4, 16: capacity/8, 24: capacity/16, 32 : capacity/32}, entropyLimit = 0.8)
table.load('topics.csv')
env.process(table.display(100))
env.run(until=run_time)
#quit()
#tab0 = [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 5, 6, 7, 8, 9, 9]
#tab1 = [1, 0, 1, 0, 1, 0, 1, 0]
#tab2 = [1, 1, 1, 1, 0, 0, 0, 0, 2]
#tab3 = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
#print("Entropy", get_entropy(tab0))
#print("Entropy", get_entropy(tab1))
#print("Entropy", get_entropy(tab2))
#print("Entropy", get_entropy(tab3))
#quit()
#tree = Tree()
#in_file = open('../ips1k.txt', "r")
#counter = 0
#x = []
#y = []
#for line in in_file:
#    addr = line.rstrip()
#    addr_tab = addr.split('.')
#    print(">>>", addr, "->", '{0:08b}'.format(int(addr_tab[0])) + '.' + '{0:08b}'.format(int(addr_tab[1])) + '.' + '{0:08b}'.format(int(addr_tab[2])) + '.'+ '{0:08b}'.format(int(addr_tab[3])))
#    y.append(tree.add(addr))
#    x.append(counter)
#    counter += 1

#fig, ax = plt.subplots()
#ax.plot(x, y)
#ax.set_yscale('log')
#print(sum(y)/len(y))
#plt.show()
#tree.add("127.0.0.1")
#tree.add("127.0.0.1")
#print("~~~~~~~~~~~~~~~~~~~~~~")
