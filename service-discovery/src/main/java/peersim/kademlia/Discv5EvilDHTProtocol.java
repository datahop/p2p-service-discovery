package peersim.kademlia;

/**
 * Discv5 Ticket Evil Protocol implementation.
 *
 */ 
import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;

import peersim.config.Configuration;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;
import peersim.edsim.EDProtocol;
import peersim.edsim.EDSimulator;
import peersim.transport.UnreliableTransport;
import peersim.kademlia.KademliaCommonConfig;
import peersim.kademlia.KademliaNode;
import peersim.kademlia.Message;
import peersim.kademlia.operations.TicketOperation;
import peersim.kademlia.TicketTable;

public class Discv5EvilDHTProtocol extends Discv5DHTProtocol {

    // VARIABLE PARAMETERS
    final String PAR_ATTACK_TYPE = "attackType";
    final String PAR_NUMBER_OF_REGISTRATIONS = "numberOfRegistrations";
    
    // type of attack (TopicSpam)
    private String attackType;
    // number of registrations to make

    private boolean first=true;
    private HashMap<Topic, ArrayList<TopicRegistration>> evilTopicTable;
	private RoutingTable evilRoutingTable; // routing table only containing evil neighbors
	private HashMap <Topic, HashMap<BigInteger,Long> >initTicketRequestTime;
	private HashMap <Topic, HashMap<BigInteger,Long> >previousTicketRequestTime;

    /**
     * Replicate this object by returning an identical copy.<br>
     * It is called by the initializer and do not fill any particular field.
     * 
     * @return Object
     */
    public Object clone() {
        Discv5EvilDHTProtocol dolly = new Discv5EvilDHTProtocol(Discv5EvilDHTProtocol.prefix);
        return dolly;
    }
    
    /**
     * Used only by the initializer when creating the prototype. Every other instance call CLONE to create the new object.
     * 
     * @param prefix
     *            String
     */
    public Discv5EvilDHTProtocol(String prefix) {
        super(prefix);
        this.attackType = Configuration.getString(prefix + "." + PAR_ATTACK_TYPE);

        this.evilTopicTable = new HashMap<Topic, ArrayList<TopicRegistration>>();
		this.evilRoutingTable = new RoutingTable(KademliaCommonConfig.NBUCKETS,KademliaCommonConfig.K,KademliaCommonConfig.MAXREPLACEMENT);
        // logger is not initialised at this point
        if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID)) 
            System.out.println("Attacker type Hybrid");
        else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_MALICIOUS_REGISTRAR))
            System.out.println("Attacker type Malicious Registrar");
        else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM))
            System.out.println("Attacker type Topic Spam");
        else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_DOS))
            System.out.println("Attacker type Dos");
        else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
            System.out.println("Attacker type waiting time spam");
			this.initTicketRequestTime = new HashMap<>();
			this.previousTicketRequestTime = new HashMap<>();

        }
        else {
            System.out.println("Invalid attacker type");
            System.exit(1);
        }
    }
	
    /**
	 * This procedure is called only once and allow to inizialize the internal state of KademliaProtocol. Every node shares the
	 * same configuration, so it is sufficient to call this routine once.
	 */
	protected void _init() {
		// execute once
		if (_ALREADY_INSTALLED)
			return;

		super._init();
	}


    /**
     * Start a register topic operation.<br>
     * If this is an on-going register operation with a previously obtained 
     * ticket, then send a REGTOPIC message; otherwise,
     * Find the ALPHA closest node and send REGTOPIC message to them
     * 
     * @param m
     *            Message received (contains the node to find)
     * @param myPid
     *            the sender Pid
     */
    protected void handleInitRegister(Message m, int myPid) {
        Topic t = (Topic) m.body;
        
        logger.warning("In handleInitRegister of EVIL "+t.getTopic()+" "+t.getTopicID());
        

        if(this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_DOS)) {
        // if only a spammer than follow the normal protocol
            //super.handleInitRegisterTopic(m, myPid);
            return;
        }
        if(this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
        	HashMap<BigInteger,Long> init = new HashMap<BigInteger,Long>();
            initTicketRequestTime.put(t,init);
            //logger.warning("Log"+initTicketRequestTime.get(t).ge);
            previousTicketRequestTime.put(t, new HashMap<BigInteger,Long>());
            
            super.handleInitRegister(m, myPid);
        }
        if ( first && ( this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID) || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_MALICIOUS_REGISTRAR) ) ) {
            first = false;
            logger.warning("Filling up the topic table with malicious entries");
            for (int i = 0; i < Network.size(); i++) {
                Node n = Network.get(i);
                KademliaProtocol prot = (KademliaProtocol) n.getKademliaProtocol();
                if(this.getNode().equals(prot.getNode()))
                    continue; //skip this node
                if (prot.getNode().is_evil) { //add a registration to evilTopicTable
                    TopicRegistration reg = new TopicRegistration(prot.getNode());
                    Topic targetTopic = prot.getTargetTopic();
                    ArrayList<TopicRegistration> regList = this.evilTopicTable.get(targetTopic);
                    if (regList != null)
                        regList.add(reg);
                    else {
                        regList = new ArrayList<TopicRegistration>();
                        this.evilTopicTable.put(targetTopic, regList);
                    }
                }
            }
        }

        // Fill the evilRoutingTable only with other malicious nodes
        this.evilRoutingTable.setNodeId(this.node.getId());
        for (int i = 0; i < Network.size(); i++) {
            Node n = Network.get(i);
            KademliaProtocol prot = (KademliaProtocol) n.getKademliaProtocol();
            if(this.getNode().equals(prot.getNode()))
                continue;
            if (prot.getNode().is_evil) {
                this.evilRoutingTable.addNeighbour(prot.getNode().getId());   
            }
        }

        super.handleInitRegister(m, myPid);

        /*
        if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM) || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID) ) {
            
            if(!ticketTables.containsKey(t.getTopicID())) {
                KademliaObserver.addTopicRegistration(t, this.node.getId());
                int k = (int) Math.ceil((double) this.targetNumOfRegistrations / KademliaCommonConfig.NBUCKETS);
        	    TicketTable rou = new TicketTable(KademliaCommonConfig.NBUCKETS,k,10,this,t,myPid,false);
                rou.setNodeId(t.getTopicID());
                ticketTables.put(t.getTopicID(),rou);
            
                for(int i = 0; i<= KademliaCommonConfig.BITS;i++) {
                    BigInteger[] neighbours = routingTable.getNeighbours(i);
                    //if(neighbours.length!=0)logger.warning("Bucket at distance "+i+" with "+neighbours.length+" nodes");
                    //else logger.warning("Bucket at distance "+i+" empty");
                    this.numOfRegistrations += 1;
                    rou.addNeighbour(neighbours);
                }
            }
            if (this.numOfRegistrations < this.targetNumOfRegistrations) {
                logger.warning("Failed to send " + this.targetNumOfRegistrations + " registrations - only sent " + this.numOfRegistrations);
            }
            //sendLookup(t,myPid);
        }
        else {
            super.handleInitRegisterTopic(m, myPid);
        }*/
    }
    

    /**
     * Process a topic query message.<br>
     * The body should contain a topic. Return a response message containing
     * the registrations for the topic and the neighbors close to the topic.
     * 
     * @param m
     *            Message received (contains the node to find)
     * @param myPid
     *            the sender Pid
     */
    protected void handleTopicQuery(Message m, int myPid) {
    	
        Topic t = (Topic) m.body;
        TopicRegistration[] registrations = new TopicRegistration[0];

        if(this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)||this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_DOS)||this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
        // if only a spammer than follow the normal protocol
            super.handleTopicQuery(m, myPid);
        }
        else {
            ArrayList<TopicRegistration> regList = this.evilTopicTable.get(t);
            if(regList != null && !regList.isEmpty()) {
                registrations = (TopicRegistration []) regList.toArray(new TopicRegistration[regList.size()]);
            }
        
            int result_len = KademliaCommonConfig.K > registrations.length ? registrations.length : KademliaCommonConfig.K;
            TopicRegistration[] final_results = new TopicRegistration[result_len];

            for (int i = 0; i < result_len; i++) 
                final_results[i] = registrations[CommonState.r.nextInt(registrations.length)];
            
            BigInteger[] neighbours = this.evilRoutingTable.getNeighbours(Util.distance(t.getTopicID(), this.node.getId()));

            /*Message.TopicLookupBody body = new Message.TopicLookupBody(final_results, neighbours);
            Message response  = new Message(Message.MSG_TOPIC_QUERY_REPLY, body);
            response.operationId = m.operationId;
            response.src = this.node;
            response.ackId = m.id; 
            logger.warning(" responds with Malicious TOPIC_QUERY_REPLY");
            sendMessage(response, m.src.getId(), myPid);*/
            
            
    		Message.TopicLookupBody body = new Message.TopicLookupBody(registrations, neighbours);
    		Message response  = new Message(Message.MSG_TOPIC_QUERY_REPLY, body);
    		response.operationId = m.operationId;
    		response.src = this.node;
    		assert m.src != null;
    		response.dest = m.src;
    		response.ackId = m.id; 
    		logger.info(" responds with TOPIC_QUERY_REPLY");
    		sendMessage(response, m.src.getId(), myPid);
        }
    }
    
  
    /**
     *  Process register requests
     *  The malicious node simply approves all tickets
     *
     */
    protected void handleRegister(Message m, int myPid) {
        super.handleRegister(m, myPid);
        /*
		Ticket ticket = (Ticket) m.body;
        ticket.setRegistrationComplete(true);
        
        Message response  = new Message(Message.MSG_REGISTER_RESPONSE, ticket);
        response.ackId = ticket.getMsg().id;
        response.operationId = ticket.getMsg().operationId;
        sendMessage(response, ticket.getSrc().getId(), myPid);*/
    }

	/**
	 * Response to a route request.<br>
	 * Respond with only K-closest malicious peers 
	 * 
	 * @param m
	 *            Message
	 * @param myPid
	 *            the sender Pid
	 */
	protected void handleFind(Message m, int myPid, BigInteger dist) {
		
		
		logger.warning("Handle find evil");
    	if(this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)||this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_DOS)||this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
            super.handleFind(m, myPid,dist);
            return;
    	}
		// get the ALPHA closest node to destNode
        this.evilRoutingTable.setNodeId(this.node.getId());
		BigInteger[] neighbours = this.evilRoutingTable.getNeighbours(dist);

		/*System.out.print("Including neigbours: [");
		for(BigInteger n : neighbours){
			System.out.println(", " + n);
		}
		System.out.println("]");*/


		// create a response message containing the neighbours (with the same id of the request)
		Message response = new Message(Message.MSG_RESPONSE, neighbours);
		response.operationId = m.operationId;
		//response.body = m.body;
		response.src = this.node;
		response.dest = m.src; 
		response.ackId = m.id; // set ACK number

		// send back the neighbours to the source of the message
		sendMessage(response, m.src.getId(), myPid);
	}

    /**
     * manage the peersim receiving of the events
     * 
     * @param myNode
     *            Node
     * @param myPid
     *            int
     * @param event
     *            Object
     */
    public void processEvent(Node myNode, int myPid, Object event) {

        //super.processEvent(myNode, myPid, event);
        Message m;
        
        SimpleEvent s = (SimpleEvent) event;
        if (s instanceof Message) {
            m = (Message) event;
            m.dest = this.node;
        }
        
        //TODO we could simply let these "handle" calls made in the parent class
        switch (((SimpleEvent) event).getType()) {
            
            case Message.MSG_INIT_REGISTER:
                m = (Message) event;
                handleInitRegister(m, myPid);
                break;

            case Message.MSG_TOPIC_QUERY:
                m = (Message) event;
                handleTopicQuery(m, myPid);
                break;

            default :
                super.processEvent(myNode, myPid, event);
        }
    }
}
