import math
import matplotlib.pyplot as plt

from Tree import *




def flip(b):
    assert(b == '0' or b == '1')
    if (b == '0'):
        return '1'
    return '0'

# generates a specified amount of IPs that will get the lowest possible score in the IP tree
def generate_IPs(n):
    ips = []
    init_ip = list('1'*32)
    for i in range(0, n):
        for j in range(0, len(init_ip)):
            if((i % (2**j)) == 0):
                init_ip[j] = flip(init_ip[j])
        
        ip_str = ''
        for octet in range(0, 4):
            offset = octet*8
            octet_str = str(int(''.join(init_ip[offset:offset + 8]), 2))
            ip_str  = ip_str + '.' + octet_str
        #remove the first '.'
        ips.append(ip_str[1:])
    return ips

ips = generate_IPs(1000)
print(ips)
print("There are",len(ips), "items and", len(set(ips)), "distinct items.")

tree = Tree()
#ips = ['0.0.0.0', '0.0.0.0', '0.0.0.0']
scores = []
fig = plt.figure()
ax = fig.add_subplot()

counter = 0
for ip in ips:
    score = tree.add(ip)
    print("added:", ip, "with score:", score)
    print("######################################################")
    ax.scatter(2*counter, score, label='benign', color='green')
    

    score = tree.add(ips[counter%1])
    ax.scatter(2*counter + 1, score, label='malicious', color='red')
    counter += 1


malicious_ips = ips[0:10]



plt.show()
quit()


class Model:

    def __init__(self):
        self.capacity = 10
        self.table = {}
        self.counter = 0
        self.ad_lifetime = 10

    def get_id_modifier(self, iD, table):
        current_ids = [x['id'] for x in table.values()]
        return math.pow(((current_ids.count(iD))/len(table)), 0.2)
    def get_basetime(self, table):
        return (30*self.ad_lifetime)/math.pow(1-len(table)/self.capacity, 5)


    def add(self, req):
        self.table[self.counter] = req
        self.counter += 1

    def get_waiting_time(self, ID):
        table = self.table
        if(len(table) > 0):
            base_waiting_time = self.get_basetime(table)
            id_modifier = self.get_id_modifier(ID, table)
            return base_waiting_time * id_modifier
        else:
            return 0


m = Model()
print(m.get_waiting_time('id1'))

req = {'id': 'id1'}
m.add(req)
print(m.get_waiting_time('id1'))

req = {'id': 'id2'}
m.add(req)
print(m.get_waiting_time('id1'))