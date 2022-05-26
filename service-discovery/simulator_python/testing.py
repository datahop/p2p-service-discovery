from Tree import *
import matplotlib.pyplot as plt
import math
from numpy import random
import pandas as pd

def plot_multi(data, cols=None, spacing=.1, **kwargs):

    from pandas import plotting

    # Get default color style from pandas - can be changed to any other color list
    if cols is None: cols = data.columns
    if len(cols) == 0: return
    #colors = getattr(getattr(plotting, '_style'), '_get_standard_colors')(num_colors=len(cols))
    colors = ['green', 'blue', 'orange', 'red', 'black', 'brown']

    # First axis
    ax = data.loc[:, cols[0]].plot(label=cols[0], color=colors[0], style= '-', **kwargs)
    ax.set_ylabel(ylabel=cols[0])
    lines, labels = ax.get_legend_handles_labels()

    print(cols)
    counter = 1
    for col in cols[1:]:
        print("index")
        ax_new = ax.twinx()
        ax_new.spines['right'].set_position(('axes', counter))
        data.loc[:, cols[counter]].plot(ax=ax_new, label=cols[counter], style= '--',  color=colors[counter % len(colors)])
        ax_new.set_ylabel(ylabel=cols[counter])
        counter += 1
        line, label = ax_new.get_legend_handles_labels()
        lines += line
        labels += label

    #return ax
    # Multiple y-axes
    #ax_new = ax.twinx()
    #ax_new.spines['right'].set_position(('axes', 1))
    #data.loc[:, cols[0]].plot(ax=ax_new, label=cols[0], style= '--',  color=colors[0 % len(colors)])
    #ax_new.set_ylabel(ylabel=cols[0])

        # Proper legend position
    

    ax.legend(lines, labels, loc=0)

    return ax

def get_entropy_modifier(topics, topic):
        current_topic_entropy = get_entropy(topics)
        new_topics = topics + [topic]
        new_topic_entropy = get_entropy(new_topics)
        print(topics)
        if((len(topics)) == 0):
            topic_modifier = 1
        elif(new_topic_entropy == 0):
            topic_modifier = 2
        else:
            topic_modifier = current_topic_entropy/new_topic_entropy

        print("old->new_entropy:", current_topic_entropy, "->", new_topic_entropy, "new - old:", new_topic_entropy - current_topic_entropy, "new/old:", new_topic_entropy/current_topic_entropy, "modifier:", topic_modifier)
        topic_modifier = max(topic_modifier, 1)
        return topic_modifier
        #return new_topic_entropy

def get_polynomial_modifier(topics, topic, power):
    count = topics.count(topic)
    return math.pow(count/size, power)*100

def get_occupancy_modifier(topics, topic, power):
    count = topics.count(topic)
    return 1/math.pow(1-(count/size), power)

def test_topic_modifier(inputs):
    modifiers = {}
    #modifiers['n'] = list(range(0, len(inputs[list(inputs)[0]])))
    for input_name in inputs.keys():
        topics = []
        input = inputs[input_name]
        powers = [4, 1, 2, 0.5, 0.1]
        for power in powers:
            modifiers['occupancy_' + str(power) + input_name] = []
            topics = []
            for item in input:
                #modifiers['entropy_'+input_name].append(get_entropy_modifier(topics, item))
                #modifiers['polynomial_' + str(power) + input_name].append(get_polynomial_modifier(topics, item, power))
                modifiers['occupancy_' + str(power) + input_name].append(get_occupancy_modifier(topics, item, power))
                topics.append(item)
        
            
    #print("Input:", input)
    print("Modifiers:", modifiers)

    #df = pd.DataFrame(modifiers)
    #df.set_index('n', inplace=True)
    #print(df)
    #plot_multi(df, figsize=(6, 3))
    #plt.show()

    figure, ax = plt.subplots()
    for key in modifiers.keys():
        ax.plot(range(0, len(modifiers[key])), modifiers[key], label=key)
    
    ax.legend()
    ax.set_title("Modifiers")
    ax.set_yscale('log')
    plt.show()


class OldTable:
    def __init__(self):
        self.counters = {}
        self.counter_total = 0
    
    def add(self, ip):
        if(ip not in self.counters):
            self.counters[ip] = 0
        same_ip = self.counters[ip]
        total = self.counter_total
        self.counters[ip] += 1
        self.counter_total += 1

        if(total == 0):
            return 0
        else:
            return same_ip/total


def test_ip_modifier(input):
    modifiers = {}
    modifiers['n'] = []# = list(range(0, len(inputs[list(inputs)[0]])))
    modifiers['type'] = []
    modifiers['val'] = []
    modifiers['input'] = []
    
    for input_name in inputs.keys():
        input = inputs[input_name]

        counter = 0
        tree = Tree(exp=False)
        for item in input:
            modifiers['n'].append(counter)
            modifiers['type'].append('sum')
            modifiers['val'].append(tree.add(item))
            modifiers['input'].append(input_name)
            counter += 1
        
        counter = 0
        table = Tree(exp=True)
        for item in input:
            modifiers['n'].append(counter)
            modifiers['type'].append('exp')
            modifiers['val'].append(table.add(item))
            modifiers['input'].append(input_name)
            counter += 1

    print("Modifiers:", modifiers)
    df = pd.DataFrame(modifiers)
    #df.set_index('n', inplace=True)
    print(df)

    figure, ax = plt.subplots()
    for type_key,type_group in df.groupby('type'):
        if(type_key == 'exp'):
            style = '-'
        else:
            style = '--'
        for input_key, input_group in type_group.groupby('input'):
            print(type_key, input_key)
            print(input_group)
            input_group.plot(x='n', y='val', ax=ax, style=style, linewidth = 5, label = type_key + "/" + input_key)

    #plot_multi(df, figsize=(6, 3))
    plt.show()

size = 10


inputs = {}
#inputs['all_same'] = ['10.0.0.1']*size
#inputs['one_different'] = ['10.0.0.1']*size
#inputs['one_different'][int(size/5)] = '255.255.255.255 '
#inputs['one_different'][int(size/5)+1] = '255.255.255.255 '
#inputs['regular'] = []
ip_file = open('./workloads/ips.txt', "r")
for i in range(0, size):
    ip = ip_file.readline().rstrip()
    #inputs['regular'].append(ip)
ip_file.close()

inputs['regular_malicious'] = []
ip_file = open('./workloads/ips.txt', "r")
malicious = []
for i in range(1, size):
    #malicious.append(str(i*10) + "." +  str(i*10) + "." +  str(i*10) + "." +  str(i*10))
    malicious.append("192.168.0."+str(i))

for i in range(0, size):
    if(i%2 == 0):
        inputs['regular_malicious'].append(malicious[i%len(malicious)])    
    else:
        ip = ip_file.readline().rstrip()
        inputs['regular_malicious'].append(ip)

inputs['malicious_only'] = []
for i in range(0, size):
        inputs['malicious_only'].append(malicious[i%len(malicious)])    

print(inputs)
#quit()

test_ip_modifier(inputs)