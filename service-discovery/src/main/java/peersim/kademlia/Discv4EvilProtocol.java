package peersim.kademlia;


import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.HashMap;

import peersim.config.Configuration;
import peersim.core.Cleanable;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;
import peersim.edsim.EDSimulator;
import peersim.kademlia.operations.FindOperation;
import peersim.kademlia.operations.LookupOperation;
import peersim.kademlia.operations.Operation;
import peersim.kademlia.operations.RegisterOperation;
import peersim.kademlia.operations.TicketOperation;
import peersim.transport.UnreliableTransport;




public class Discv4EvilProtocol extends Discv4Protocol  {

	//public TopicTable topicTable;
	private RoutingTable evilRoutingTable; // routing table only containing evil neighbors

	
	public Discv4EvilProtocol(String prefix) {
		
		super(prefix);
		this.evilRoutingTable = new RoutingTable(KademliaCommonConfig.NBUCKETS,KademliaCommonConfig.K,KademliaCommonConfig.MAXREPLACEMENT);

		
	}
	
	/**
	 * Replicate this object by returning an identical copy.<br>
	 * It is called by the initializer and do not fill any particular field.
	 * 
	 * @return Object
	 */
	public Object clone() {
		Discv4EvilProtocol dolly = new Discv4EvilProtocol(Discv4EvilProtocol.prefix);
		return dolly;
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

		logger.warning("Discv4 evil handleInitRegister");

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
    }
    
	/**
	 * Response to a route request.<br>
	 * Respond with the peers in your k-bucket closest to the key that is being looked for
	 * 
	 * @param m
	 *            Message
	 * @param myPid
	 *            the sender Pid
	 */
	protected void handleFind(Message m, int myPid, BigInteger dist) {
		// get the ALPHA closest node to destNode
		
		logger.warning("Discv4 evil handleFind");

		BigInteger[] neighbours = this.evilRoutingTable.getNeighbours(dist);
		//System.out.println("find node received at "+this.node.getId()+" distance "+(int) m.body); 

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
	 * set the current NodeId
	 * 
	 * @param tmp
	 *            BigInteger
	 */
	public void setNode(KademliaNode node) {
		super.setNode(node);
		
	}
	
	public void onKill() {
		// System.out.println("Node removed");
		//topicTable = null;
	}
	
	/*private void handleTimeout(Timeout t, int myPid){
		logger.warning("Handletimeout");
		
	}*/
	
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
	/**
	 * manage the peersim receiving of the events
	 * 
	 * @param myNode Node
	 * @param myPid  int
	 * @param event  Object
	 */
	public void processEvent(Node myNode, int myPid, Object event) {

		logger.info("Discv4 evil process event");
		super.processEvent(myNode, myPid, event);
		Message m;


		SimpleEvent s = (SimpleEvent) event;
		if (s instanceof Message) {
			m = (Message) event;
			m.dest = this.node;
		}

		switch (((SimpleEvent) event).getType()) {


		case Message.MSG_INIT_REGISTER:
			m = (Message) event;
			handleInitRegister(m, myPid);
			break;


		}
	}
	
}
