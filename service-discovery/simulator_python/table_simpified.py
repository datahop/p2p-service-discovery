#!/usr/bin/python3
import csv
from matplotlib import cm
import matplotlib.pyplot as plt
import math
import abc
import numpy as np
from scipy.stats import entropy
import copy
from random import randint
import simpy
from copy import deepcopy
from Tree import *

class Table(metaclass=abc.ABCMeta):
    def __init__(self, capacity, ad_lifetime, interval=1):
        self.capacity = capacity
        self.ad_lifetime = ad_lifetime
        self.interval = interval
        

        self.table = {}
        self.tree = Tree()
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
        
    #overloaded by the DiversityTable class
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

    #remove an add when it expires
    def remove_ad(self, ad_id, delay):
        yield self.env.timeout(delay)
        self.log("Removing", self.table[ad_id])
        req = self.table.pop(ad_id)
        
        ip_addr = req['ip']
        self.tree.removeAndPropagateUp(ip_addr, self.env.now)
        
        trie_node = self.tree.lookupAddress(ip_addr)
        if trie_node.getCounter() > 1:
            score = self.tree.remove(ip_addr)
            assert(score >= 0)
        else: # if counter is 1, we can remove the trie node when the current bound expires
            removal_time = max(0,trie_node.getBound() - (self.env.now - trie_node.getTimestamp()))
            self.env.process(self.remove_lower_bound(removal_time, ip=ip_addr))

        id = req['id']
        self.id_counter[id]['counter'] -= 1
        #schedule lowe bound removal when we remove the last entry
        if(self.id_counter[id]['counter'] == 0):
            #wait with the removal to make it safe
            removal_time = max(0, self.id_counter[id]['wtime'] - (self.env.now - self.id_counter[id]['timestamp']))
            self.env.process(self.remove_lower_bound(removal_time, id=id))
        assert(self.id_counter[req['id']]['counter'] >= 0)

        topic = req['topic']
        self.topic_counter[topic]['counter'] -= 1
        #schedule lowe bound removal when we remove the last entry
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

        #admit the registrant right away
        if(waiting_time == 0):
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

            #schedule add removal
            self.env.process(self.remove_ad(self.ad_ids, self.ad_lifetime))
            self.ad_ids += 1
            
            #make the registrant re-register when its add expire
            new_req = copy.deepcopy(req)
            del new_req['req_id']
            new_req['expire'] = 0
            new_req['arrived'] = self.env.now + self.ad_lifetime
            new_req['returned'] = 0
            self.env.process(self.new_request(new_req, self.ad_lifetime))

        #the registrant still has to wait for time indicated in the ticket
        else:
            req['returned'] += 1
            self.log("Need to wait for", waiting_time)
            #"impatient" spamming clients
            if(req['attack'] == 3):
                self.env.process(self.new_request(req, min(500, waiting_time)))
            else:
                self.env.process(self.new_request(req, waiting_time))
    
    
class DiversityTable(Table):
    def __init__(self, capacity, ad_lifetime, amplify = 1, occupancy_power = 10, ip_id_power = 0.1, topic_power = 10, base_multiplier = 10):
        super().__init__(capacity, ad_lifetime)
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
            print("Base wtime:", wtime, "bound:", bound)
            if(bound < wtime):
                print("In if")
                self.base_counter['wtime'] = wtime
                self.base_counter['timestamp'] = self.env.now
            return max(wtime, bound)
        else:
            return 0

    #the Tree implementation is in Tree.py
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

        assert bound >= boundGT, 'Trie-based lower-bound must NOT be smaller than ground truth value'
        return max(wtime, bound)

    def get_id_modifier(self, iD, table):
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


    #returns calculated_time - time_registrant_already_waited
    def get_waiting_time(self, req):
        table  = deepcopy(self.table)
        waited_time = (self.env.now - req['arrived'])
        needed_time = 0
        missing_time = 0

        base_modifier = self.get_base_modifier(table)
        topic_modifier = self.get_topic_modifier(req['topic'], table)
        id_modifier = self.get_id_modifier(req['id'], table)
        ip_modifier = self.get_ip_modifier(req['ip'], table)
        needed_time =  sum([base_modifier, topic_modifier, id_modifier, ip_modifier])
        print("needed_time:", needed_time, "base_modifier:", base_modifier, "ip_modifier:", ip_modifier, "id_modifier:", id_modifier, "topic_modifier:", topic_modifier)
        missing_time = max(0, needed_time - waited_time)

        #tell registrant to come back after ad_lifetime
        #if the waiting time is > ad_lifetime
        return min(missing_time, self.ad_lifetime)
