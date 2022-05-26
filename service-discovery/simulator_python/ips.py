#!/usr/bin/python3

import pandas as pd
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from numpy import genfromtxt
import numpy as np
import array
import sys
import csv
import math
import socket
import struct


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


if (len(sys.argv) < 2):
    print("Provide at least one file")
    exit(1)


#get file object
in_file = open(sys.argv[1], "r")
x = []
y = []
#traverse through lines one by one
min = 999999999999999
min_ip = ""
max = 0
max_ip = ""
counter = 0
x.append(ip2int("1.0.0.0"))
y.append(counter)
for line in in_file:
    addr = line.rstrip()[1:]
    val = ip2int(addr)
    #print(addr, val)
    x.append(val)
    y.append(counter)
    if(val < min):
        min = val
        min_ip = addr
    if(val > max):
        max = val
        max_ip = addr
    counter += 1

in_file.close()
print("min", min, "min_ip", min_ip)
print("max", max, "max_ip", max_ip)
plt.scatter(x, y)
plt.show()
