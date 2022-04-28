features = {'size': {'type': 'benign', 'default': 5000, 'keyword': 'SIZE', 'vals':[1000, 2000,5000]},
            'topic': {'type': 'benign', 'default': 20, 'keyword': 'control.0traffic.maxtopicnum', 'vals':[1, 40]},
            'discv5regs': {'type': 'benign', 'default': 5, 'keyword': 'protocol.3kademlia.TICKET_TABLE_BUCKET_SIZE', 'vals':[1, 3]},
            'idDistribution': {'type': 'attack', 'default': 'uniform', 'defaultAttack': 'uniform', 'keyword': 'init.1uniqueNodeID.idDistribution', 'vals':['nonUniform','uniform']},
            'sybilSize': {'type': 'attack', 'default': 0, 'defaultAttack': 10, 'keyword': 'init.1uniqueNodeID.iPSize', 'vals':[1, 10, 50]},
            'attackTopic': {'type': 'attack', 'default': 0, 'defaultAttack': 5, 'keyword': 'init.1uniqueNodeID.attackTopic', 'vals':[1, 5]},
            'percentEvil': {'type': 'attack', 'default': 0, 'defaultAttack': 0.1, 'keyword':'init.1uniqueNodeID.percentEvil', 'vals':[0.05, 0.1, 0.2]}
        }

benign_y_vals = ['registrationMsgs', 'lookupMsgs', 'discovered', 'wasDiscovered', 'regsPlaced', 'regsAccepted', 'lookupAskedNodes']

attack_y_vals = ['percentageMaliciousDiscovered', 'percentageEclipsedLookups']

#protocols to test
config_files = {'discv5': './config/discv5ticket.cfg', 
                'dhtTicket': './config/discv5dhtticket.cfg', 
                'dht': './config/discv5dhtnoticket.cfg', 
                'discv4' : './config/noattackdiscv4.cfg',
                'attackDiscv5' :  './config/attack_configs/discv5ticketattack.cfg',
                'attackDhtTicket' : './config/attack_configs/discv5dhtticket_topicattack.cfg',
                'attackDht' : './config/attack_configs/discv5dhtnoticket_topicattack.cfg',
                'attackDiscv4' : './config/attack_configs/discv4_topicattack.cfg'}

#security
features_attack = {}

result_dir = './python_logs'


titlePrettyText = {'registrationMsgs' : 'Number of Registration Messages', 
              'lookupMsgs': 'Number of Lookup Messages', 
              'discovered' : 'Number of Discovered Peers', 
              'wasDiscovered': 'Number of Times Discovered by Others',
              'lookupAskedNodes' : 'Number of Contacted Nodes during Lookups', 
              'percentageEclipsedLookups': 'Percentage of Eclipsed Lookups', 
              'percentageMaliciousDiscovered' : 'Percentage of Malicious Nodes Returned from Lookups', 
              'regsPlaced': 'Number of Registrations Placed',
              'regsAccepted':'Number of Registrations Accepted'
              }

protocolPrettyText = {'dht':'DHT',
                      'dhtTicket': 'DHT_Ticket',
                      'discv5' : 'TBSD',
                      'discv4' : 'Discv4'
                      }
