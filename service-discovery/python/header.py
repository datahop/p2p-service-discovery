features = {'size': {'type': 'benign', 'default': 25000, 'keyword': 'SIZE', 'vals':[5000, 25000, 50000]},
            'topic': {'type': 'benign', 'default': 300, 'keyword': 'control.0traffic.maxtopicnum', 'vals':[50,300,600]},
            'discv5regs': {'type': 'benign', 'default': 3, 'keyword': 'protocol.3kademlia.TICKET_TABLE_BUCKET_SIZE', 'vals':[3]},
            'idDistribution': {'type': 'attack', 'default': 'uniform', 'defaultAttack': 'uniform', 'keyword': 'init.1uniqueNodeID.idDistribution', 'vals':['nonUniform','uniform']},
            'sybilSize': {'type': 'attack', 'default': 0, 'defaultAttack': 10, 'keyword': 'init.1uniqueNodeID.iPSize', 'vals':[1, 10, 100]},
            'attackTopic': {'type': 'attack', 'default': 0, 'defaultAttack': 0, 'keyword': 'init.1uniqueNodeID.attackTopic', 'vals':[0,5,9]},
            'percentEvil': {'type': 'attack', 'default': 0, 'defaultAttack': 1.0, 'keyword':'init.1uniqueNodeID.percentEvil', 'vals':[1.0, 2.0, 3.0]}}

benign_y_vals = ['totalMsg','registrationMsgs', 'lookupMsgs', 'discovered', 'wasDiscovered', 'regsPlaced', 'regsAccepted', 'lookupAskedNodes']

attack_y_vals = ['percentageMaliciousDiscovered', 'percentageEclipsedLookups', 'lookupAskedMaliciousNodes','maliciousResultsByHonest']


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


titlePrettyText = {'registrationMsgs' : '#Registration Messages', 
              'totalMsg' : '#Total received messages',
              'lookupMsgs': '#Lookup Messages', 
              'discovered' : '#Discovered Peers', 
              'wasDiscovered': '#Times Discovered by Others',
              'lookupAskedNodes' : '#Contacted Nodes during Lookups', 
              'percentageEclipsedLookups': 'Eclipsed Lookups', 
              'percentageMaliciousDiscovered' : 'Percentage of Malicious Nodes Returned from Lookups', 
              'regsPlaced': '#Registrations Placed',
              'regsAccepted':'#Registrations Accepted',
              'lookupAskedMaliciousNodes': '#lookups to malicious nodes',
              'maliciousResultsByHonest': '#malicious results by honest nodes'
              }

protocolPrettyText = {'dht':'DHT',
                      'dhtTicket': 'DHT_Ticket',
                      'discv5' : 'TBSD',
                      'discv4' : 'Discv4'
                      }

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
