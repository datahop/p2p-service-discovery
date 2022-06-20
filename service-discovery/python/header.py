features = {'size': {'type': 'benign', 'default': 25000, 'keyword': 'SIZE', 'vals':[5000,25000,50000]},
            'topic': {'type': 'benign', 'default': 300, 'keyword': ['control.0traffic.maxtopicnum', 'init.1uniqueNodeID.topicnum'], 'vals':[100,300,600]},
            'discv5regs': {'type': 'benign', 'default': 3, 'keyword': 'protocol.3kademlia.TICKET_TABLE_BUCKET_SIZE', 'vals':[3]},
            'idDistribution': {'type': 'attack', 'default': 'uniform', 'defaultAttack': 'nonUniform', 'keyword': 'init.1uniqueNodeID.idDistribution', 'vals':['uniform','nonUniform']},
            'sybilSize': {'type': 'attack', 'default': 0, 'defaultAttack': 100, 'keyword': 'init.1uniqueNodeID.iPSize', 'vals':[10,100,1000]},
            'attackTopic': {'type': 'attack', 'default': 0, 'defaultAttack': 0, 'keyword': 'init.1uniqueNodeID.attackTopic', 'vals':[0]},
            'percentEvil': {'type': 'attack', 'default': 0, 'defaultAttack': 0.02, 'keyword':'init.1uniqueNodeID.percentEvil', 'vals':[0.01,0.02,0.04]}}

benign_y_vals = ['totalMsg','registrationMsgs', 'lookupMsgs', 'discovered', 'wasDiscovered', 'regsPlaced', 'regsAccepted', 'lookupAskedNodes']

attack_y_vals = ['percentageMaliciousDiscovered', 'percentageEclipsedLookups', 'lookupAskedMaliciousNodes','maliciousResultsByHonest']


#protocols to test
config_files = {'TOPDISC': './config/discv5ticket.cfg', 
                'DHTTicket': './config/discv5dhtticket.cfg', 
                'DHT': './config/discv5dhtnoticket.cfg', 
                'DISCv4' : './config/noattackdiscv4.cfg'}
#config_files = {'attackTOPDISC' :  './config/attack_configs/discv5ticketattack.cfg',
#                'attackDHTTicket' : './config/attack_configs/discv5dhtticket_topicattack.cfg',
#                'attackDHT' : './config/attack_configs/discv5dhtnoticket_topicattack.cfg',
#                'attackDISCv4' : './config/attack_configs/discv4_topicattack.cfg'}

#security
features_attack = {}

result_dir = './python_logs'


titlePrettyText = {'registrationMsgs' : '#Registration messages', 
              'totalMsg' : '#Total received messages',
              'lookupMsgs': '#Lookup messages', 
              'discovered' : '#Discovered peers', 
              'wasDiscovered': '#Times discovered by others',
              'lookupAskedNodes' : '#Contacted nodes during lookups', 
              'percentageEclipsedLookups': '%Eclipsed lookups', 
              'percentageMaliciousDiscovered' : '%Malicious nodes returned from lookups', 
              'regsPlaced': '#Registrations placed',
              'regsAccepted':'#Registrations accepted',
              'lookupAskedMaliciousNodes': '#Lookups to malicious nodes',
              'maliciousResultsByHonest': '#Malicious results by honest nodes',
              'percentEvilTopic' : 'Ratio of topic peers that are malicious',
              'percentEvil' : '#Malicious nodes',         
              'sybilSize' : '#IP addresses used by attackers',
              'attackTopic' : 'Attacked topic',
              'idDistribution' : 'Distribution of attacker IDs',
              'size': '#Nodes in the network',
              'topic': '#Topics in the network',
              'idDistribution': 'Sybil nodes identifiers distribution',
              'discv5regs': 'discv5regs'
              }

protocolPrettyText = {'dht':'dht',
                      'dhtTicket': 'dhtTicket',
                      'discv4' : 'discv4',
                      'discv5' : 'TOPDISC'
                      }

ticksPrettyText = {}
#ticksPrettyText = {'percentEvil':['250','500','1000']}

y_lims = {#'violin_size_discovered': 100,
          'violin_size_lookupMsgs': 500,
          'violin_size_registrationMsgs': 10000,
          'violin_size_regsAccepted': 4000,
          'violin_topic_lookupMsgs': 500,
          'violin_topic_registrationMsgs': 10000,
          'violin_topic_regsAccepted': 4000,
          'violin_topic_wasDiscovered': 100,
          'violin_topic_totalMsg':9000,
          'violin_size_totalMsg':9000
          }
