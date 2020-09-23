package peersim.kademlia;

/**
 * Discv5 Protocol implementation.
 *
 */ 
import java.math.BigInteger;
import java.util.LinkedHashMap;
import java.util.TreeMap;

import peersim.kademlia.Topic;

import java.util.Arrays;

import peersim.config.Configuration;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;
import peersim.edsim.EDProtocol;
import peersim.edsim.EDSimulator;
import peersim.transport.UnreliableTransport;
import peersim.kademlia.KademliaNode;

public class Discv5TicketProtocol extends KademliaProtocol {

    /**
	 * Topic table of this node
	 */
    public Discv5TopicTable topicTable;

    /**
     * topic radius computer
     */
    private TopicRadius topicRadius;
	
	/**
	 * Replicate this object by returning an identical copy.<br>
	 * It is called by the initializer and do not fill any particular field.
	 * 
	 * @return Object
	 */
	public Object clone() {
		Discv5TicketProtocol dolly = new Discv5TicketProtocol(Discv5TicketProtocol.prefix);
		return dolly;
	}
	
    /**
	 * Used only by the initializer when creating the prototype. Every other instance call CLONE to create the new object.
	 * 
	 * @param prefix
	 *            String
	 */
	public Discv5TicketProtocol(String prefix) {
		super(prefix);
        this.topicTable = new Discv5TopicTable();
    }


	/**
	 * schedule sending a message after a given delay  with current transport layer and starting the timeout timer (which is an event) if the message is a request 
	 * 
	 * @param m
	 *            the message to send
	 * @param destId
	 *            the Id of the destination node
	 * @param myPid
	 *            the sender Pid
     * @param delay
     *            the delay to wait before sending           
	 */
	public void scheduleSendMessage(Message m, BigInteger destId, int myPid, long delay) {
		Node src = nodeIdtoNode(this.node.getId());
		Node dest = nodeIdtoNode(destId);
        
        m.src = this.node;
        m.dest = new KademliaNode(destId);     
		
        logger.info("-> (" + m + "/" + m.id + ") " + destId);

        // TODO: remove the assert later
	    //assert(src == this.node);

		//System.out.println(this.kademliaNode.getId() + " (" + m + "/" + m.id + ") -> " + destId);

		transport = (UnreliableTransport) (Network.prototype).getProtocol(tid);
        long network_delay = transport.getLatency(src, dest);
        EDSimulator.add(network_delay+delay, m, dest, myPid); 

		if ( (m.getType() == Message.MSG_FIND) || (m.getType() == Message.MSG_REGISTER)|| (m.getType() == Message.MSG_TICKET_REQUEST) ) { 
			Timeout t = new Timeout(destId, m.id, m.operationId);

			// add to sent msg
			this.sentMsg.put(m.id, m.timestamp);
			EDSimulator.add(delay+4*network_delay, t, src, myPid); 
		}
    }

	
	/**
	 * send a message with current transport layer and starting the timeout timer (which is an event) if the message is a request
	 * 
	 * @param m
	 *            the message to send
	 * @param destId
	 *            the Id of the destination node
	 * @param myPid
	 *            the sender Pid
	 */
	public void sendMessage(Message m, BigInteger destId, int myPid) {
		// add destination to routing table
		this.routingTable.addNeighbour(destId);

        m.src = this.node;
        m.dest = new KademliaNode(destId);     
		Node src = nodeIdtoNode(this.node.getId());
		Node dest = nodeIdtoNode(destId);

		logger.info("-> (" + m + "/" + m.id + ") " + destId);

		transport = (UnreliableTransport) (Network.prototype).getProtocol(tid);
		transport.send(src, dest, m, kademliaid);
		KademliaObserver.msg_sent.add(1);

		if ( (m.getType() == Message.MSG_FIND) || (m.getType() == Message.MSG_REGISTER)|| (m.getType() == Message.MSG_TICKET_REQUEST) ) { 
			Timeout t = new Timeout(destId, m.id, m.operationId);
			long latency = transport.getLatency(src, dest);

			// add to sent msg
			this.sentMsg.put(m.id, m.timestamp);
			EDSimulator.add(4 * latency, t, src, myPid); // set delay = 2*RTT
		}
	}

    private void makeRegisterDecision(Topic topic, int myPid) {

        long curr_time = CommonState.getTime();
        Ticket [] tickets = this.topicTable.makeRegisterDecisionForTopic(topic, curr_time);
        
        for (Ticket ticket : tickets) {
            Message m = ticket.getMsg();
            if (ticket.isRegistrationComplete()) {
                handleFind(m, myPid, Util.logDistance(ticket.getTopic().getTopicID(), this.node.getId()));
            }
            else {
                Message response  = new Message(Message.MSG_REGISTER_RESPONSE, ticket);
                response.ackId = m.id;
                response.operationId = m.operationId;
                sendMessage(response, ticket.getSrc().getId(), myPid);
            }
        }
    }
    /**
     * 
     *
     */
    private void handleRegister(Message m, int myPid) {
		Ticket ticket = (Ticket) m.body;
        topicTable.register_ticket(ticket, m);
		
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
    private void handleTopicQuery(Message m, int myPid) {
		Topic t = (Topic) m.body;
		TopicRegistration[] registrations = this.topicTable.getRegistration(t);
		BigInteger[] neighbours = this.routingTable.getNeighbours(Util.prefixLen(this.node.getId(), t.getTopicID()));
		
		Message.TopicLookupBody body = new Message.TopicLookupBody(registrations, neighbours);
		Message response  = new Message(Message.MSG_TOPIC_QUERY_REPLY, body);
		response.operationId = m.operationId;
		response.src = this.node;
		response.ackId = m.id; 
		logger.info(" responds with TOPIC_QUERY_REPLY");
		//System.out.println(" responds with TOPIC_QUERY_REPLY");
		sendMessage(response, m.src.getId(), myPid);
    
    }
    /**
     * Process a ticket request
     *
     */
    private void handleTicketRequest(Message m, int myPid) {
        //FIXME add logs
        long curr_time = CommonState.getTime();
		//System.out.println("Ticket request received: " + m.src.getId());
        Topic topic = (Topic) m.body;
        KademliaNode advertiser = new KademliaNode(m.src); 
        //System.out.println("TicketRequest handle "+topic.getTopic());
		transport = (UnreliableTransport) (Network.prototype).getProtocol(tid);
        long rtt_delay = 2*transport.getLatency(nodeIdtoNode(m.src.getId()), nodeIdtoNode(m.dest.getId()));
        Ticket ticket = topicTable.getTicket(topic, advertiser, rtt_delay, curr_time);

        // Setup a timeout event for the registration decision
        if (ticket.getWaitTime() >= 0) {
            Timeout timeout = new Timeout(topic);
            EDSimulator.add(rtt_delay + ticket.getWaitTime() + KademliaCommonConfig.ONE_UNIT_OF_TIME, timeout, nodeIdtoNode(this.node.getId()), myPid);
        }
        // Send a response message with a ticket back to advertiser
        Message response = new Message(Message.MSG_TICKET_RESPONSE, ticket);
		response.ackId = m.id; // set ACK number
		response.operationId = m.operationId;
        sendMessage(response, m.src.getId(), myPid);
    }

    /**
     * Process a ticket response and schedule a register message
     *
     */
    private void handleTicketResponse(Message m, int myPid) {
    	//System.out.println("handleTicketResponse: " + m.src);
        Ticket t = (Ticket) m.body;
        if (t.getWaitTime() == -1) 
        {   
            System.out.println("Attempted to re-register topic on the same node");
            return;
        }
        Message register = new Message(Message.MSG_REGISTER, t);
		register.ackId = m.id; // set ACK number
        register.dest = new KademliaNode(m.src);
        register.body = m.body;
        register.operationId = m.operationId;
        scheduleSendMessage(register, m.src.getId(), myPid, t.getWaitTime());
    }

	/**
	 * Process a register response message.<br>
	 * The body should contain a ticket, which indicates whether registration is 
     * complete. In case it is not, schedule sending a new register request
	 * 
	 * @param m
	 *            Message received (contains the node to find)
	 * @param myPid
	 *            the sender Pid
	 */
    private void handleRegisterResponse(Message m, int myPid) {
        Ticket ticket = (Ticket) m.body;
        Topic topic = ticket.getTopic();
        if (ticket.isRegistrationComplete() == false) {
        	System.out.println("Unsuccessful Registration of topic: " + ticket.getTopic() + " at node: " + m.src.toString() + " wait time: " + ticket.getWaitTime());
            Message register = new Message(Message.MSG_REGISTER, ticket);
            register.operationId = m.operationId;
            register.body = m.body;
            scheduleSendMessage(register, m.src.getId(), myPid, ticket.getWaitTime());
        }
        else {
            System.out.println("This should not happen!");
        }
    }

	/**
	 * Start a register topic opearation.<br>
	 * If this is an on-going register operation with a previously obtained 
     * ticket, then send a REGTOPIC message; otherwise,
     * Find the ALPHA closest node and send REGTOPIC message to them
	 * 
	 * @param m
	 *            Message received (contains the node to find)
	 * @param myPid
	 *            the sender Pid
	 */
    private void handleInitRegisterTopic(Message m, int myPid) {
        
        Topic t = (Topic) m.body;
        t.setHostID(this.node.getId());
		
        KademliaObserver.addTopicRegistration(t.getTopic(), this.node.getId());


        //System.out.println("Neighbors: " + Arrays.toString(neighbours));
        //System.out.println("My id is: " + this.kademliaNode.getId().toString());
        //System.out.println("Target id is: " + targetAddr.toString());

        TicketOperation top = new TicketOperation(m.timestamp, t);
		top.body = m.body;
		operations.put(top.operationId, top);
        
        // Lookup the target address in the routing table
		BigInteger[] neighbours = this.routingTable.getNeighbours(Util.logDistance((BigInteger) t.getTopicID(), this.node.getId()));
		
        if(neighbours.length<KademliaCommonConfig.K)
			neighbours = this.routingTable.getKClosestNeighbours(KademliaCommonConfig.K);

        top.elaborateResponse(neighbours); 
		top.available_requests = KademliaCommonConfig.ALPHA;
		
        // set message operation id
		m.operationId = top.operationId;
		m.type = Message.MSG_TICKET_REQUEST;
		m.src = this.node;

		// send ALPHA messages
		for (int i = 0; i < KademliaCommonConfig.ALPHA; i++) {
			BigInteger nextNode = top.getNeighbour();
			if (nextNode != null) {
                Message ticket_request = m.copy();
                scheduleSendMessage(ticket_request, nextNode, myPid, 0); 
				top.nrHops++;
			}
			else {
				System.err.println("In register Returned neighbor is NUll !");
				//System.exit(-1);
			}
		}
    }
	
    /**
	 * Start a topic query opearation.<br>
	 * 
	 * @param m
	 *            Message received (contains the node to find)
	 * @param myPid
	 *            the sender Pid
	 */
    
    private void handleInitTopicLookup(Message m, int myPid) {
		KademliaObserver.lookup_total.add(1);

		Topic t = (Topic) m.body;
		
        LookupOperation lop = new LookupOperation(m.timestamp, t);
		lop.body = m.body;
		operations.put(lop.operationId, lop);
	
		//BigInteger[] neighbours = this.routingTable.getNeighbours((BigInteger) m.body, this.node.getId());
		BigInteger[] neighbours = this.routingTable.getNeighbours(Util.logDistance((BigInteger) t.getTopicID(), this.node.getId()));
		
        if(neighbours.length<KademliaCommonConfig.K)
			neighbours = this.routingTable.getKClosestNeighbours(KademliaCommonConfig.K);
		lop.elaborateResponse(neighbours);
		lop.available_requests = KademliaCommonConfig.ALPHA;
	
		// set message operation id
		m.operationId = lop.operationId;
		m.type = Message.MSG_TOPIC_QUERY;
		m.src = this.node;
	
		// send ALPHA messages
		for (int i = 0; i < KademliaCommonConfig.ALPHA; i++) {
			BigInteger nextNode = lop.getNeighbour();
			if (nextNode != null) {
				sendMessage(m.copy(), nextNode, myPid);
				lop.nrHops++;
                //System.out.println("Topic lookup for: " + t);
			}
			else {
				System.err.println("In Topic Lookup Returned neighbor is NUll !");
				//System.exit(-1);
			}
		}
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
        
		//this.discv5id = myPid;
		super.processEvent(myNode, myPid, event);
        Message m;

	    SimpleEvent s = (SimpleEvent) event;
        if (s instanceof Message) {
	        m = (Message) event;
            m.dest = this.node;
	    	KademliaObserver.reportMsg((Message) s, false);
        }
		
        switch (((SimpleEvent) event).getType()) {

			case Message.MSG_TOPIC_QUERY_REPLY:
				m = (Message) event;
				sentMsg.remove(m.ackId);
				find(m, myPid);
				break;

            case Message.MSG_REGISTER:
                m = (Message) event;
                handleRegister(m, myPid);
                break;

            case Message.MSG_REGISTER_RESPONSE:
                m = (Message) event;
				sentMsg.remove(m.ackId);
                handleRegisterResponse(m, myPid);
                break;

            case Message.MSG_TOPIC_QUERY:
                m = (Message) event;
                handleTopicQuery(m, myPid);
                break;
			
            case Message.MSG_INIT_TOPIC_LOOKUP:
				m = (Message) event;
				handleInitTopicLookup(m, myPid);
				break;

            case Message.MSG_INIT_REGISTER:
                m = (Message) event;
                handleInitRegisterTopic(m, myPid);
                break;
            
            case Message.MSG_TICKET_REQUEST:
                m = (Message) event;
                handleTicketRequest(m, myPid);
                break;
            
            case Message.MSG_TICKET_RESPONSE:
                m = (Message) event;
				sentMsg.remove(m.ackId);
                handleTicketResponse(m, myPid);
                break;

            case Timeout.TICKET_TIMEOUT:
                Topic t = ((Timeout)event).topic;
                makeRegisterDecision(t, myPid);
                break;


			/*case Timeout.TIMEOUT: // timeout
				Timeout t = (Timeout) event;
				if (sentMsg.containsKey(t.msgID)) { // the response msg didn't arrived
					System.out.println("Node " + this.kademliaNode.getId() + " received a timeout: " + t.msgID + " from: " + t.node);
					// remove form sentMsg
					sentMsg.remove(t.msgID);
					// remove node from my routing table
					this.routingTable.removeNeighbour(t.node);
					// remove from closestSet of find operation
					this.fop.closestSet.remove(t.node);
				}
				break;*/
        }
    }
	
    /**
	 * set the current NodeId
	 * 
	 * @param tmp
	 *            BigInteger
	 */
	public void setNode(KademliaNode node) {
		this.topicTable.setHostID(node.getId());
		super.setNode(node);
	}

}
