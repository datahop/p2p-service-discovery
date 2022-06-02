#!/usr/bin/python3
import csv
from matplotlib import cm
import matplotlib.pyplot as plt
import math
import abc
import numpy as np
from scipy.stats import entropy
import copy
import random as rand
import simpy
import sys
from copy import deepcopy
from Tree import *
from TreeMichal import *
from TreeOnur import *

class Table(metaclass=abc.ABCMeta):
    def __init__(self, capacity, ad_lifetime, interval=1, seed=1, tree = 'default'):
        rand.seed(seed)
        self.capacity = capacity
        self.ad_lifetime = ad_lifetime
        self.interval = interval
    
        self.table = {}
        if(tree == 'default'):
            self.tree = Tree()
        elif(tree == 'michal'):
            self.tree = TreeMichal()
        elif(tree == 'onur'):
            self.tree = TreeOnur()
        else:
            print("Unknown tree type", tree)
            sys.exit(-1)
        self.workload = {}
        self.env = simpy.Environment()
        self.ad_ids = 0
        self.admission_times = []
        self.occupancies = {}
        self.occupancies_by_attackers = {}
        self.per_topic_occupancies = {}
        self.per_topic_occupancies_by_attackers = {}
        self.returns = []
        
        self.req_counter = 0
        self.pending_req = {}
        self.honest_count = 0
        self.malicious_count = 0
        self.malicious_in = {}
        self.honest_in = {}

        self.ip_counter = {}
        self.id_counter = {}
        self.topic_counter = {}
        self.base_counter = {}
        self.base_counter['wtime'] = 0
        self.base_counter['timestamp'] = 0

    #Loads a file with arriving requests
    #each line is a seperate arriving ticket/registration request
    def load(self, file):
        counter = 0
        self.input_file = file
        with open(file, newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
            for row in reader:
                #count malicious and benign registrations for statistics
                if 'attack' in row.keys():
                    row['attack'] = int(row['attack'])
                    if(row['attack'] == 0):
                        self.honest_count += 1
                    else:
                        self.malicious_count += 1
                #read the arrival time from the file or
                #assign increasing ones automatically
                if 'time' in row.keys():
                    row['arrived'] = float(row['time'])
                else:
                    row['arrived'] = counter
                row['returned'] = 0

                self.workload[counter] = row
                #schedule arrival of the requests in the simulator
                if 'time' in row.keys():
                    self.env.process(self.new_request(row, float(row['time'])))
                else:
                    self.env.process(self.new_request(row, counter * self.interval))
                counter += 1

    #run the simmulation       
    def run(self, runtime):
        self.report_occupancy()
        self.env.run(until=runtime)
        
    #periodically report the state of the table
    def report_occupancy(self):
        #yield self.env.timeout(1)
        if(len(self.occupancies) > 0):
            self.occupancies[self.env.now-1]  = list(self.occupancies.values())[-1]
        self.occupancies[self.env.now] = len(self.table) / self.capacity
        
        attacker_entries = [req for req in self.table.values() if req['attack'] != 0]
        honest_entries = [req for req in self.table.values() if req['attack'] == 0]
        if(len(self.occupancies_by_attackers) > 0):
            self.occupancies_by_attackers[self.env.now-1] = list(self.occupancies_by_attackers.values())[-1]
        self.occupancies_by_attackers[self.env.now] = len(attacker_entries) / self.capacity

        if(self.malicious_count > 0):
            if(len(self.malicious_in) > 0):
                self.malicious_in[self.env.now - 1] = list(self.malicious_in.values())[-1]
            self.malicious_in[self.env.now] = len(attacker_entries)/self.malicious_count
        
        if(self.honest_count > 0):
            if(len(self.honest_in) > 0):
                self.honest_in[self.env.now - 1] = list(self.honest_in.values())[-1]
            self.honest_in[self.env.now] = len(honest_entries)/self.honest_count
        #self.env.process(self.report_occupancy())

    #plotting helper
    def scatter(self, values, title, ax = None, color_map = None):
        if(ax == None):
            fig, ax = plt.subplots()
        cmap = cm.get_cmap('Spectral')
        vals = list(set(values))
        #print("vals:",   vals)
        #required for consistent coloring across graphs
        if(color_map == None):
            if(len(vals) > 0):
                step = 1/len(vals)
            color_map = {}
            for item in vals:
                color_map[item] = cmap(vals.index(item) * step)

        row_length = int(math.sqrt(len(values)))
        colors = []
        x = []
        y = []
        counter = 0
        for entry in values:
            colors.append(color_map[entry])
            x.append(counter % row_length)
            y.append(int(counter/row_length))
            counter += 1
        #hack for the final report - remove later on as
        #it clashes with the code above
        colors = []
        for i in values:
            if i == 1:
                colors.append('r')
            else:
                colors.append('g')
        ax.scatter(x, y, c=colors)
        ax.set_title(title)
        #print("Frequency of", title, {x:values.count(x) for x in values})
        return color_map

    #reporting helper
    def display(self, delay):
        print("display, env", self.env)
        self.env.process(self.display_body(delay))

    #reporting helper
    def display_body(self, delay):
        yield self.env.timeout(delay)
        figure, axis = plt.subplots(2, 4)

        requests_table = [x['attack'] for x in self.table.values()]
        requests_workload = [x['attack'] for x in self.workload.values()]
        color_map = self.scatter(requests_workload, "Requests in the workload" , axis[1, 0])
        self.scatter(requests_table, "Requests in the table at", axis[0, 0], color_map)
        axis[0, 1].scatter([x[0] for x in self.admission_times], [x[1] for x in self.admission_times], c=get_colors([x[2] for x in self.admission_times]))
        axis[0, 1].set_title("Waiting times")
        #axis[2, 0].set_yscale('log')
        #print("!!!!!!!!!!!!!!!!!!", self.occupancies)
        axis[1, 1].plot(list(self.occupancies.keys()), list(self.occupancies.values()), color='b')
        #print("~~~~~~~~~~~~~~~~~~", self.occupancies_by_attackers)
        #quit()
        axis[1, 1].plot(list(self.occupancies_by_attackers.keys()), list(self.occupancies_by_attackers.values()), color='r')
        axis[1, 1].plot(list(self.occupancies.keys()), [x - y for x, y in zip(self.occupancies.values(), self.occupancies_by_attackers.values())], color='g')
        axis[1, 1].set_title("Occupancy over time")
        axis[0, 2].scatter([x[0] for x in self.returns], [x[1] for x in self.returns], c=get_colors([x[2] for x in self.returns]))
        axis[0, 2].set_title("Returns")

        # plot top-k (most registered) topics and their num. of registrations in a bar chart
        k = 5
        width = 0.10 
        sorted_topics_by_registration = {k: v for k, v in sorted(self.per_topic_occupancies.items(), key=lambda item: item[1], reverse=True)}
        topics = list(sorted_topics_by_registration.keys())[0:k]
        x_values = [x-width/2 for x in range(1, len(topics)+1)]
        good_regs = [self.per_topic_occupancies[x] for x in topics]
        axis[0, 3].bar(x_values, good_regs, color='g')
        evil_regs = []
        for topic in topics:
            if topic in self.per_topic_occupancies_by_attackers:
                evil_regs.append(self.per_topic_occupancies_by_attackers[topic])
            else:
                evil_regs.append(0)
        x_values = [x+width/2 for x in range(1, len(topics)+1)]
        axis[0, 3].bar(x_values, evil_regs, color='r')
        axis[0, 3].set_ylabel('Number of registrations')
        axis[0, 3].set_xlabel('Topics')
        axis[0, 3].set_xticks(x_values)
        axis[0, 3].set_xticklabels(topics)
        print('Topics: ', topics, ' per_topic_normal: ', self.per_topic_occupancies, ' per_topic attacker: ', self.per_topic_occupancies_by_attackers)

        figure, ax = plt.subplots()
        ax.plot(list(self.honest_in.keys()), list(self.honest_in.values()), c='g')
        ax.plot(list(self.malicious_in.keys()), list(self.malicious_in.values()), c='r')
        ax.set_title("Percentage of overal requests in the table")
        axis[1, 2].plot(list(self.honest_in.keys()), list(self.honest_in.values()), c='g')
        axis[1, 2].plot(list(self.malicious_in.keys()), list(self.malicious_in.values()), c='r')
        axis[1, 2].set_title("Percentage of overal requests in the table")

        print("Occupancy_total", self.extract_total(self.occupancies))
        print("Malicious total", self.extract_total(self.occupancies_by_attackers))

    #reporting helper
    def add_stats(self, delay, stats):
        self.env.process(self.add_stats_body(delay, stats))

    #reporting helper
    def extract_total(self, dict):
        labels = []
        sizes = []
        for val in set(dict.values()):
            l = []
            for key in dict.keys():
                if(dict[key] == val):
                    l.append(key)
            interval = []
            for i in range(2, len(l)-1, 2):
                interval.append(l[i+1] - l[i])
            labels.append(val)
            sizes.append(sum(interval))
        total = 0
        for i in range(0, len(sizes)):
            total += labels[i] * (sizes[i] / sum(sizes))
        return total
    
    #reporting helper
    def add_stats_body(self, delay, stats):
        yield self.env.timeout(delay)
        total = self.extract_total(self.occupancies)
        total_malicious = self.extract_total(self.occupancies_by_attackers)
        total_honest = total - total_malicious

        stats['table'].append(type(self).__name__)
        #stats['malicious_count'].append(self.malicious_count)
        stats['capacity'].append(self.capacity)
        stats['occupancy_total'].append(total)
        stats['malicious_occupancy_total'].append(total_malicious)
        stats['honest_occupancy_total'].append(total_honest)
        stats['ad_lifetime'].append(self.ad_lifetime)
        stats['occupancy_power'].append(self.occupancy_power)
        stats['ip_id_power'].append(self.ip_id_power)
        stats['topic_power'].append(self.topic_power)
        print("sum:", total)

    #reporting helper
    def log(self, *arg):
        print("[", self.env.now, "s]",  sep="", end='')
        print(*arg)
    
    @abc.abstractmethod
    def get_waiting_time(self, req):
        pass

    def remove_lower_bound(self, delay, id=None, ip = None, topic = None):
        yield self.env.timeout(delay)

        #if 'counter' > 0 it means that in the meantime we added a new entry 
        # with this ID to the table and have to cancel the lower bound removal
        if((id != None) and (id in self.id_counter) and (self.id_counter[id]['counter'] == 0)):
            del self.id_counter[id]

        #ditto
        if((topic != None) and (topic in self.topic_counter) and  (self.topic_counter[topic]['counter'] == 0)):
            del self.topic_counter[topic]

        #if (ip is not None):
        #    nextTime = self.tree.remove(ip, self.env.now)
        #    if nextTime > 0:
        #        self.env.process(self.remove_lower_bound(nextTime, ip=ip))
        

    #remove an add when it expires
    def remove_ad(self, ad_id, delay):
        yield self.env.timeout(delay)
        self.log("Removing", self.table[ad_id])
        req = self.table.pop(ad_id)
        
        ip_addr = req['ip']
        #nextTime = self.tree.remove(ip_addr, self.env.now)
        #if nextTime > 0:
        #    self.env.process(self.remove_lower_bound(nextTime, ip=ip_addr))
        self.tree.removeAndPropagateUp(ip_addr, self.env.now)
        
        id = req['id']
        self.id_counter[id]['counter'] -= 1
        #schedule lower bound removal of id when we remove the last entry
        if(self.id_counter[id]['counter'] == 0):
            #wait with the removal to make it safe
            removal_time = max(0, self.id_counter[id]['wtime'] - (self.env.now - self.id_counter[id]['timestamp']))
            self.env.process(self.remove_lower_bound(removal_time, id=id))
        assert(self.id_counter[req['id']]['counter'] >= 0)

        topic = req['topic']
        self.topic_counter[topic]['counter'] -= 1
        #schedule lower bound removal of topic when we remove the last entry
        if(self.topic_counter[topic]['counter'] == 0):
            #wait with the removal to make it safe
            removal_time = max(0, self.topic_counter[topic]['wtime'] - (self.env.now - self.topic_counter[topic]['timestamp']))
            self.env.process(self.remove_lower_bound(removal_time, topic=topic))
        assert(self.topic_counter[topic]['counter'] >= 0)        
        
        self.report_occupancy()

    #process an incoming request
    def new_request(self, req, delay):
        yield self.env.timeout(delay)
        
        if('req_id' in req):
            self.log("-> old request arrived:", req)
        else:
            req['req_id'] = self.req_counter
            self.req_counter += 1
            self.log("-> new request arrived:", req)
            assert(req['req_id'] not in self.pending_req)
            self.pending_req[req['req_id']] = req

        waiting_time = int(self.get_waiting_time(req))
        self.admission_times.append((self.env.now, waiting_time, req['attack']))

        if(waiting_time == 0):
            self.log("Admitting right away")
            del self.pending_req[req['req_id']]
            req['expire'] = self.env.now + self.ad_lifetime
            self.table[self.ad_ids] = req
            
            #update lower bounds for each modifier
            if(req['id'] not in self.id_counter):
                self.id_counter[req['id']] = {}
                self.id_counter[req['id']]['counter'] = 0
                self.id_counter[req['id']]['wtime'] = 0
                self.id_counter[req['id']]['timestamp'] = 0
            self.id_counter[req['id']]['counter'] += 1

            self.tree.add(req['ip'])
            if(req['ip'] not in self.ip_counter):
                self.ip_counter[req['ip']] = {}
                self.ip_counter[req['ip']]['wtime'] = 0
                self.ip_counter[req['ip']]['timestamp'] = 0

            if(req['topic'] not in self.topic_counter):
                self.topic_counter[req['topic']] = {}
                self.topic_counter[req['topic']]['counter'] = 0
                self.topic_counter[req['topic']]['wtime'] = 0
                self.topic_counter[req['topic']]['timestamp'] = 0
            self.topic_counter[req['topic']]['counter'] += 1

            if req['attack']:
                if req['topic'] in self.per_topic_occupancies_by_attackers:
                    self.per_topic_occupancies_by_attackers[ req['topic'] ] += 1
                else:
                    self.per_topic_occupancies_by_attackers[ req['topic'] ] = 1
            else:
                if req['topic'] in self.per_topic_occupancies:
                    self.per_topic_occupancies[ req['topic'] ] += 1
                else:
                    self.per_topic_occupancies[ req['topic'] ] = 1

            self.env.process(self.remove_ad(self.ad_ids, self.ad_lifetime))
            self.ad_ids += 1
            #self.admission_times.append((self.env.now, self.env.now - req['arrived'], req['attack']))
            self.returns.append((self.env.now, req['returned'], req['attack']))
            self.report_occupancy()
            
            #make the registrant re-register when its add expire
            # add a random time between 0 and 99 milliseconds
            #just to make the simulation more realistic
            rand_time = rand.randint(0, 99)
            new_req = copy.deepcopy(req)
            del new_req['req_id']
            new_req['expire'] = 0
            new_req['arrived'] = self.env.now + self.ad_lifetime + rand_time
            new_req['returned'] = 0
            self.env.process(self.new_request(new_req, self.ad_lifetime + rand_time))

        #the registrant still has to wait for time indicated in the ticket
        else:
            req['returned'] += 1
            self.log("Need to wait for", waiting_time)
            #"impatient" spamming clients
            if(req['attack'] == 3):
                self.env.process(self.new_request(req, min(500, waiting_time)))
            else:
                self.env.process(self.new_request(req, waiting_time))
    

class SimpleTable(Table):
    def get_waiting_time(self, req):
        if(len(self.table) >= self.capacity):
            return list(self.table.items())[0][1]['expire'] - self.env.now + 1
        else:
            return 0
    
    
class DiversityTable(Table):
    def __init__(self, capacity, ad_lifetime, amplify = 1, occupancy_power = 10, ip_id_power = 0.1, topic_power = 10, base_multiplier = 10, seed=1, tree = 'default'):
        rand.seed(seed)
        super().__init__(capacity, ad_lifetime, tree=tree)
        #self.tree = Tree()
        self.ip_modifiers = {}
        self.id_modifiers = {}
        self.topic_modifiers = {}
        self.base_modifiers = {}
        self.amplify = amplify
        self.occupancy_power = occupancy_power
        self.ip_id_power = ip_id_power
        self.topic_power = topic_power
        self.base_multiplier = base_multiplier
    
    def get_base_modifier(self, table):
        modifier = 0
        if( len(table) > 0):
            modifier = 1/10000000
            bound = max(0, self.base_counter['wtime'] - (self.env.now - self.base_counter['timestamp']))
            wtime = modifier * self.get_basetime(table)
            print("Time:", self.env.now, " Base wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                print("In if")
                self.base_counter['wtime'] = wtime
                self.base_counter['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0


    def get_ip_modifier(self, ip, table):
        #print("Get IP Modifier", self.ip_counter)
        modifier, bound = self.tree.tryAdd(ip, self.env.now)

        boundGT = 0 # ground truth for bound using per-ip state
        if(ip in self.ip_counter):
            boundGT = max(0, self.ip_counter[ip]['wtime'] - (self.env.now - self.ip_counter[ip]['timestamp']))
        wtime = modifier * self.get_basetime(table)
        print("ip:", ip, "wtime:", wtime, "bound:", bound)
        if(bound < wtime):
            self.tree.updateBound(ip, wtime, self.env.now) 

        if (boundGT < wtime):
            if ip not in self.ip_counter:
                self.ip_counter[ip] = {}
            self.ip_counter[ip]['wtime'] = wtime
            self.ip_counter[ip]['timestamp'] = self.env.now
        #FIXME enable after initial tests
        #assert bound >= boundGT, 'Trie-based lower-bound must NOT be smaller than ground truth value'
        #bound = boundGT 
        return max(wtime, bound)

    def get_ip_modifier_bck(self, ip, table):
        #print("Get IP Modifier", self.ip_counter)
        if(ip in self.ip_counter):
            counter = self.ip_counter[ip]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            bound = max(0, self.ip_counter[ip]['wtime'] - (self.env.now - self.ip_counter[ip]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            print("ip:", ip, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                print("In if")
                self.ip_counter[ip]['wtime'] = wtime
                self.ip_counter[ip]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0
    
    def get_id_modifier(self, iD, table):
        #print("Get ID Modifier", self.id_counter)
        if(iD in self.id_counter):
            counter = self.id_counter[iD]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            bound = max(0, self.id_counter[iD]['wtime'] - (self.env.now - self.id_counter[iD]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            print("id:", iD, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                self.id_counter[iD]['wtime'] = wtime
                self.id_counter[iD]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0


    def get_topic_modifier(self, topic, table):
        if(topic in self.topic_counter):
            counter = self.topic_counter[topic]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.topic_power)
            bound = max(0, self.topic_counter[topic]['wtime'] - (self.env.now - self.topic_counter[topic]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            print("t:", topic, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                self.topic_counter[topic]['wtime'] = wtime
                self.topic_counter[topic]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0
        

    def get_basetime(self, table):
        return (self.base_multiplier*self.ad_lifetime)/math.pow(1-len(table)/self.capacity, self.occupancy_power)


    def get_waiting_time(self, req):
        #print("Table:", self.table)
        table  = deepcopy(self.table)
        waited_time = (self.env.now - req['arrived'])
        needed_time = 0
        missing_time = 0

        base_modifier = self.get_base_modifier(table)
        topic_modifier = self.get_topic_modifier(req['topic'], table)
        id_modifier = self.get_id_modifier(req['id'], table)
        ip_modifier = self.get_ip_modifier(req['ip'], table)
        #needed_time =  max(sum([topic_modifier, id_modifier, ip_modifier]), base_waiting_time * 1/1000000)
        needed_time =  sum([base_modifier, topic_modifier, id_modifier, ip_modifier])
        print("needed_time:", needed_time, "base_modifier:", base_modifier, "ip_modifier:", ip_modifier, "id_modifier:", id_modifier, "topic_modifier:", topic_modifier)
        missing_time = max(0, needed_time - waited_time)


        self.ip_modifiers[self.env.now] = (self.env.now, ip_modifier, req['attack'])
        self.id_modifiers[self.env.now] = (self.env.now, id_modifier, req['attack'])
        self.topic_modifiers[self.env.now] = (self.env.now, topic_modifier, req['attack'])
        self.base_modifiers[self.env.now] = (self.env.now, base_modifier, req['attack'])
        
        #if(req['attack'] == 0):
        #    print("needed_time:", needed_time, "base:", base_waiting_time, "ip_modifier:", ip_modifier, "id_modifier:", id_modifier, "topic_modifier:", topic_modifier)
        #    print("waited time:", waited_time)
        #    print("returning:", missing_time)
            #print("self.occupancy_power:", self.occupancy_power, "self.base_multiplier:", self.base_multiplier, "self.ad_lifetime:", self.ad_lifetime)
        #needed_time = base_waiting_time
        return min(missing_time, self.ad_lifetime)

   

    def report_modifiers(self, delay):
        yield self.env.timeout(delay)
        #print("self.topic_modifiers", self.topic_modifiers)
        #quit()
        figure, axis = plt.subplots(4, 1)
        axis[0].scatter([x[0] for x in list(self.ip_modifiers.values())], [x[1] for x in list(self.ip_modifiers.values())], c=get_colors([x[2] for x in list(self.ip_modifiers.values())]))
        axis[0].set_title("IP modifier")
        #axis[0].set_yscale('log')
        axis[1].scatter([x[0] for x in list(self.id_modifiers.values())], [x[1] for x in list(self.id_modifiers.values())], c=get_colors([x[2] for x in list(self.id_modifiers.values())]))
        axis[1].set_title("ID modifier")
        #axis[1].set_yscale('log')
        axis[2].scatter([x[0] for x in list(self.topic_modifiers.values())], [x[1] for x in list(self.topic_modifiers.values())], c=get_colors([x[2] for x in list(self.topic_modifiers.values())]))
        axis[2].set_title("Topic modifier")
        axis[3].scatter([x[0] for x in list(self.base_modifiers.values())], [x[1] for x in list(self.base_modifiers.values())], c=get_colors([x[2] for x in list(self.base_modifiers.values())]))
        axis[3].set_title("Base modifier")
        #axis[2].set_yscale('log')
        #print("Topic modifiers ys:", [x[1] for x in list(self.topic_modifiers.values())])
        #print("ip honest modifiers", list(filter(lambda x: x[2] == 0, self.ip_modifiers.values())))

        figure.suptitle("Diversity Table Modifiers")

    def display_body(self, delay):
        self.env.process(self.report_modifiers(delay))
        return super().display_body(delay)
    #    yield self.env.timeout(0)
    #    print("before super().display_body, delay:", delay)
        
    #    print("after super().display_body")
        #quit()


class DiversityTablePlain(DiversityTable):
    def get_ip_modifier(self, ip, table):
        if(ip in self.ip_counter):
            counter = self.ip_counter[ip]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            wtime = modifier * self.get_basetime(table)
            print("ip:", ip, "wtime:", wtime)
            return wtime
        else:
            return 0
    
    def get_id_modifier(self, iD, table):
        #print("Get ID Modifier", self.id_counter)
        if(iD in self.id_counter):
            counter = self.id_counter[iD]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            wtime = modifier * self.get_basetime(table)
            print("id:", iD, "wtime:", wtime)
            return wtime
        else:
            return 0


    def get_topic_modifier(self, topic, table):
        if(topic in self.topic_counter):
            counter = self.topic_counter[topic]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.topic_power)
            wtime = modifier * self.get_basetime(table)
            print("t:", topic, "wtime:", wtime)
            return wtime
        else:
            return 0


class DiversityTableRandom(DiversityTable):
    def get_ip_modifier(self, ip, table):
        #print("Get IP Modifier", self.ip_counter)
        if(ip in self.ip_counter):
            counter = self.ip_counter[ip]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            bound = max(0, self.ip_counter[ip]['wtime'] - (self.env.now - self.ip_counter[ip]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            r = rand.randint(0, int(wtime/2)) - wtime/4
            wtime = wtime + r
            print("ip:", ip, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                print("In if")
                self.ip_counter[ip]['wtime'] = wtime
                self.ip_counter[ip]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0
    
    def get_id_modifier(self, iD, table):
        #print("Get ID Modifier", self.id_counter)
        if(iD in self.id_counter):
            counter = self.id_counter[iD]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.ip_id_power)
            bound = max(0, self.id_counter[iD]['wtime'] - (self.env.now - self.id_counter[iD]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            r = rand.randint(0, int(wtime/2)) - wtime/4
            wtime = wtime + r
            print("id:", iD, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                self.id_counter[iD]['wtime'] = wtime
                self.id_counter[iD]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0


    def get_topic_modifier(self, topic, table):
        if(topic in self.topic_counter):
            counter = self.topic_counter[topic]['counter']
            modifier = 0
            if( len(table) > 0):
                modifier = math.pow((counter/(len(table)+1)), self.topic_power)
            bound = max(0, self.topic_counter[topic]['wtime'] - (self.env.now - self.topic_counter[topic]['timestamp']))
            wtime = modifier * self.get_basetime(table)
            r = rand.randint(0, int(wtime/2)) - wtime/4
            wtime = wtime + r
            print("t:", topic, "wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                self.topic_counter[topic]['wtime'] = wtime
                self.topic_counter[topic]['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0

#helper for bar charts
def get_widths(l):
    widths = []
    for i in range(0, len(l)-1):
        widths.append(l[i+1] - l[i])
    widths.append(widths[-1])
    return widths

def get_colors(l):
    colors = ['g', 'r', 'b']
    result = []
    for i in l:
        result.append(colors[i%len(colors)])
    return result
