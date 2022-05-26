from numpy import random
import csv
import random as rand

def generate_regular(size = 100, zipf_distribution = 2, rate = 1.0, seed = 0.0, output_filename = None):
    rand.seed(seed)
    random.seed(seed)
    if(output_filename == None):
        output_filename = './workloads/regular_size' + str(size) + '_dist' + str(zipf_distribution) + '.csv'
    #get ips/ids from ethereum repo
    ip_file = open('./workloads/ips.txt', "r")
    id_file = open('./workloads/ids.txt', "r")
    rand.seed(seed)
    topics = random.zipf(a=zipf_distribution, size=size)#for topics
    t_next_req = 0.0 # time of next request
    with open(output_filename, 'w') as output_file:
        fieldnames = ['time', 'id', 'ip', 'topic', 'attack']
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        for i in range(0, size):
            t_next_req += rand.expovariate(rate)
            record = {}
            ip = ip_file.readline().rstrip()
            iD = id_file.readline().rstrip()
            if(not ip or not iD):
                print("Not enough IPs/IDs in the files")
                exit(1)
            #record['time'] = int(1000*t_next_req)
            record['time'] = int(10*i)
            record['id'] = iD
            record['ip'] =ip
            record['topic'] = 't' + str(topics[i])
            record['attack'] = 0
            #print(record)
            dict_writer.writerow(record)
    print("Generated regular workload in", str(output_filename))

def generate_impatient(size = 100, zipf_distribution = 2, rate = 1.0, seed = 0.0, output_filename = None):
    rand.seed(seed)
    random.seed(seed)
    if(output_filename == None):
        output_filename = './workloads/impatient_size' + str(size) + '_dist' + str(zipf_distribution) + '.csv'
    #get ips/ids from ethereum repo
    ip_file = open('./workloads/ips.txt', "r")
    id_file = open('./workloads/ids.txt', "r")
    rand.seed(seed)
    topics = random.zipf(a=zipf_distribution, size=size)#for topics
    t_next_req = 0.0 # time of next request
    flag = True
    with open(output_filename, 'w') as output_file:
        fieldnames = ['time', 'id', 'ip', 'topic', 'attack']
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        for i in range(0, size):
            t_next_req += rand.expovariate(rate)
            record = {}
            ip = ip_file.readline().rstrip()
            iD = id_file.readline().rstrip()
            if(not ip or not iD):
                print("Not enough IPs/IDs in the files")
                exit(1)
            #record['time'] = int(1000*t_next_req)
            record['time'] = int(10*i)
            record['id'] = iD
            record['ip'] =ip
            record['topic'] = 't' + str(topics[i])
            if(flag == True):
                record['attack'] = 0
            else:
                record['attack'] = 3
            flag = not flag
            #print(record)
            dict_writer.writerow(record)
    print("Generated regular workload in", str(output_filename))

def generate_attack_topic(size = 100, zipf_distribution = 2, topic_to_attack = 't11', attacker_ip_num = 3, attacker_id_num=10, rate_normal = 1.0, rate_attack = 10.0, seed = 0.0, output_filename = None):
    rand.seed(seed)
    random.seed(seed)
    if(output_filename == None):
        output_filename = './workloads/attack_topic_size' + str(size) + '_dist' + str(zipf_distribution) + '.csv'
    #get ips/ids from ethereum repo
    ip_file = open('./workloads/ips.txt', "r")
    id_file = open('./workloads/ids.txt', "r")
    topics = random.zipf(a=zipf_distribution, size=size)#for topics

    attacker_ips = []
    for i in range(0, attacker_ip_num):
        num = int(255/attacker_ip_num * i)
        ip = str(num) + "." + str(num) + "."+ str(num) + "."+ str(num)
        attacker_ips.append(ip)
    
    attacker_ids = []
    for i in range(0, attacker_id_num):
        attacker_ids.append(''.join([str(i)]*20))
    print("attacker ips:", attacker_ips)
    print("attacker ids:", attacker_ids)

    t_next_normal_req = rand.expovariate(rate_normal)  # time of next normal request
    t_next_attack_req = rand.expovariate(rate_attack) # time of next attack request
    time = 0.0
    attack = 0
    with open(output_filename, 'w') as output_file:
        fieldnames = ['time', 'id', 'ip', 'topic', 'attack']
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        for i in range(0, size):
            if t_next_normal_req < t_next_attack_req:
                attack = 0
                time = t_next_normal_req
            elif t_next_normal_req > t_next_attack_req:
                attack = 1
                time = t_next_attack_req

            record = {}
            if( attack == 0 ):
                ip = ip_file.readline().rstrip()
                iD = id_file.readline().rstrip()
                if(not ip or not iD):
                    print("Not enough IPs/IDs in the files")
                    exit(1)
                topic = 't' + str(topics[i])
            else: # attack == 1
                ip = attacker_ips[i % attacker_ip_num]
                iD = attacker_ids[i % attacker_id_num]
                topic = topic_to_attack

            record['time'] = int(10*i)
            record['id'] = iD
            record['ip'] =ip
            record['topic'] = topic
            record['attack'] = attack
            #print(record)
            dict_writer.writerow(record)
        
            if time == t_next_normal_req:
                t_next_normal_req += rand.expovariate(rate_normal)
            if time == t_next_attack_req:
                t_next_attack_req += rand.expovariate(rate_attack)

    print("Generated regular workload in", str(output_filename))


def generate_spam_topic(size = 100, zipf_distribution = 2, attacker_ip_num = 3, attacker_id_num=10, rate_normal = 1.0, rate_attack = 10.0, seed = 0.0, output_filename = None):
    rand.seed(seed)
    random.seed(seed)
    if(output_filename == None):
        output_filename = './workloads/spam_topic_size' + str(size) + '_dist' + str(zipf_distribution) + '.csv'
    #get ips/ids from ethereum repo
    ip_file = open('./workloads/ips.txt', "r")
    id_file = open('./workloads/ids.txt', "r")
    topics = random.zipf(a=zipf_distribution, size=size)#for topics

    attacker_ips = []
    for i in range(0, attacker_ip_num):
        num = int(255/attacker_ip_num * i)
        ip = str(num) + "." + str(num) + "."+ str(num) + "."+ str(num)
        attacker_ips.append(ip)
    
    attacker_ids = []
    for i in range(0, attacker_id_num):
        attacker_ids.append(''.join([str(i)]*20))
    print("attacker ips:", attacker_ips)
    print("attacker ids:", attacker_ids)
    
    t_next_normal_req = rand.expovariate(rate_normal)  # time of next normal request
    t_next_attack_req = rand.expovariate(rate_attack) # time of next attack request
    time = 0.0
    attack = 0

    with open(output_filename, 'w') as output_file:
        fieldnames = ['time', 'id', 'ip', 'topic', 'attack']
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        for i in range(0, size):
            if t_next_normal_req < t_next_attack_req:
                attack = 0
                time = t_next_normal_req
            elif t_next_normal_req > t_next_attack_req:
                attack = 1
                time = t_next_attack_req
            record = {}
            if( attack == 0 ): # normal traffic
                ip = ip_file.readline().rstrip()
                iD = id_file.readline().rstrip()
                if(not ip or not iD):
                    print("Not enough IPs/IDs in the files")
                    exit(1)
                topic = 't' + str(topics[i])
            else: # attack traffic
                ip = attacker_ips[i % attacker_ip_num]
                iD = attacker_ids[i % attacker_id_num]
                topic = 't' + str(100+i)

            record['time'] = int(10*i) 
            record['id'] = iD
            record['ip'] =ip
            record['topic'] = topic
            record['attack'] = attack
            #print(record)
            dict_writer.writerow(record)
            if time == t_next_normal_req:
                t_next_normal_req += rand.expovariate(rate_normal)
            if time == t_next_attack_req:
                t_next_attack_req += rand.expovariate(rate_attack)
    print("Generated regular workload in", str(output_filename))

#zipf_distribution = 2
#size = 100

#generate_attack_topic(size=1000, rate_attack=2.0)
#generate_attack_topic(size=100, rate_attack=2.0)
#generate_attack_topic(size=150, rate_attack=2.0)
#generate_spam_topic(size=1000, rate_attack=2.0)
#generate_regular(size = 100, zipf_distribution=zipf_distribution)
#generate_regular(size = 10, zipf_distribution=zipf_distribution)
#generate_regular(size = 3, zipf_distribution=zipf_distribution)
