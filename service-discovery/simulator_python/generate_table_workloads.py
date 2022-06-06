from numpy import random
import csv
import random as rand


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

# helper function to flip a bit written as a string/character
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


def generate_workload(honest = 20, malicious = 80, zipf_distribution = 2, attacker_ip_num = 3, attacker_id_num=10, attack_topic = 'None', seed = 0, output_filename = None):
    size = honest + malicious
    requests = []

    if(output_filename == None):
        output_filename = './workloads/regular_size' + str(size) + '_dist' + str(zipf_distribution) + '.csv'
    random.seed(seed)
    #get ips/ids from ethereum repo
    ip_file = open('./workloads/ips.txt', "r")
    id_file = open('./workloads/ids.txt', "r")
    topics = random.zipf(a=zipf_distribution, size=honest)#for topics
    for i in range(0, honest):
        ip = ip_file.readline().rstrip()
        iD = id_file.readline().rstrip()
        assert (ip and iD), "Not enough IPs/IDs in the Ethereum files"
        topic = 't' + str(topics[i])

        record = {}
        record['time'] = 0
        record['id'] = iD
        record['ip'] =ip
        record['topic'] = topic
        record['attack'] = 0
        requests.append(record)

    malicious_ips = generate_IPs(attacker_ip_num)        
    for i in range(0, malicious):
        record = {}
        record['time'] = 0
        record['id'] = i % attacker_id_num
        record['ip'] = malicious_ips[i%len(malicious_ips)]
        if(attack_topic):
            record['topic'] = attack_topic
        else:
            record['topic'] = 'm' + str(i)
        record['attack'] = 1
        requests.append(record)
    
    with open(output_filename, 'w') as output_file:
        fieldnames = ['time', 'id', 'ip', 'topic', 'attack']
        dict_writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        dict_writer.writeheader()
        assert(size == len(requests))
        for i in range(0, size):
            req = requests.pop(rand.randint(0, len(requests) - 1))
            req['time'] = i*10
            dict_writer.writerow(req)


generate_workload(honest=5, malicious=10, attack_topic = None, output_filename='test.csv')