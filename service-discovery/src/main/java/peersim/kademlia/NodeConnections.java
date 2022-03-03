package peersim.kademlia;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import peersim.core.CommonState;
import peersim.core.Node;
import peersim.edsim.EDSimulator;

public class NodeConnections {
	
    
    protected int maxIncomingConnections;
    protected int maxOutgoingConnections;
    
    protected String topic;

    protected HashMap<KademliaNode,BigInteger> lookupResultBuffer;
        
    protected List<KademliaNode> incomingConnections;
    protected List<KademliaNode> outgoingConnections;
    
    private HashMap<BigInteger,Integer> sources;
    private HashMap<KademliaNode,BigInteger> used;
    
    protected KademliaNode n;
    protected boolean requested;
    
	public NodeConnections(String topic,KademliaNode n) {
		
		this.incomingConnections = new ArrayList<KademliaNode>();
        this.outgoingConnections = new ArrayList<KademliaNode>();
        //if(!n.is_evil) {
	        this.maxIncomingConnections = (int)KademliaCommonConfig.MAXCONNECTIONS*2/3;
	        this.maxOutgoingConnections = (int)KademliaCommonConfig.MAXCONNECTIONS/3;
        /*} else {
        	this.maxIncomingConnections = KademliaCommonConfig.MAXCONNECTIONS*1000;
        	this.maxOutgoingConnections = KademliaCommonConfig.MAXCONNECTIONS*1000;
        }*/
        this.lookupResultBuffer = new HashMap<>();
		this.topic = topic;
		this.requested = false;
		this.n = n;
		this.sources = new HashMap<>();
		this.used = new HashMap<>();
	}
	
	
	public boolean isRequested() {
		return requested;
	}
	
	public void setRequested(boolean req) {
		this.requested = req;
	}
	
	public void addLookupResult(HashMap<KademliaNode,BigInteger> lookupResultBuffer) {
		//System.out.println(CommonState.getTime()+" addLookupResult "+lookupResultBuffer.size());
		this.lookupResultBuffer.putAll(lookupResultBuffer);
		this.setRequested(false);
		/*for(KademliaNode node : lookupResultBuffer.keySet()) {
			System.out.println(CommonState.getTime()+" Result "+node+" origin:"+lookupResultBuffer.get(node));
		}*/
	}
	/*public void setLookupBuffer(List<KademliaNode> lookupResultBuffer) {
		this.lookupResultBuffer = lookupResultBuffer;
	}
	
	public List<KademliaNode> getLookupBuffer(){
		return new ArrayList<>(this.lookupResultBuffer.keySet());
	}*/
	
	public List<KademliaNode> getIncomingConnections() {
		return this.incomingConnections;
	}
	
	public List<KademliaNode> getOutgoingConnections() {
		return this.outgoingConnections;
	}
	
	public boolean removeIncomingNode(KademliaNode node) {
		return incomingConnections.remove(node);
	}
	
	public boolean removeOutgoingNode(KademliaNode node) {
		if(outgoingConnections.contains(node)) {
	   		//System.out.println(CommonState.getTime()+" outgoing connections removed "+(outgoingConnections.size()-1))
			sources.remove(used.get(node));
			used.remove(node);
			return outgoingConnections.remove(node);
		} else {
			return false;
		}
	}
	
	public void tryNewConnections() {
		
       		//


   		if(KademliaCommonConfig.FILTER_RESULTS==0){
   	    	while(outgoingConnections.size()<maxOutgoingConnections&&lookupResultBuffer.size()>0) {
   	    		List<KademliaNode> valuesList = new ArrayList<KademliaNode>(lookupResultBuffer.keySet());

        		int n = CommonState.r.nextInt(lookupResultBuffer.size());
           		KademliaNode randomNode = valuesList.get(n);
       			boolean success = startConnection(randomNode);

				if(success) {
					addOutgoingConnection(randomNode);

				}
				lookupResultBuffer.remove(randomNode);
   	    	}

   		} else {
   			//System.out.println(CommonState.getTime()+" filter results");
   			HashSet<BigInteger> valuesSources = new HashSet<BigInteger>(lookupResultBuffer.values());
   				
			while(outgoingConnections.size()<maxOutgoingConnections&&lookupResultBuffer.size()>0) {
   	    		List<KademliaNode> valuesList = new ArrayList<KademliaNode>(lookupResultBuffer.keySet());

        		int n = CommonState.r.nextInt(lookupResultBuffer.size());
           		KademliaNode randomNode = valuesList.get(n);
           		
    			if(valuesSources.size()>2||sources.keySet().size()>2||!sources.containsKey(lookupResultBuffer.get(randomNode))) {

   	       			boolean success = startConnection(randomNode);

   					if(success) {
   						addOutgoingConnection(randomNode);
   						int i=0;
   						if(sources.get(randomNode)!=null)i+=sources.get(randomNode);
   						sources.put(lookupResultBuffer.get(randomNode),i);
   						used.put(randomNode, lookupResultBuffer.get(randomNode));

   					}
   					
    			} 
				lookupResultBuffer.remove(randomNode);

   	    	}

   		} 
   			
       		//}
    	
   		//System.out.println(CommonState.getTime()+" new connections added "+count+" "+outgoingConnections.size()+" "+lookupResultBuffer.size());
        
	}

    
    protected boolean startConnection(KademliaNode node) {
    	Node nd = Util.nodeIdtoNode(node.getId());
    	//System.out.println(CommonState.getTime()+" node topic "+topic+" "+node.getTopicList().size());
    	if(!nd.isUp() || !node.hasTopic(topic)) {
    		//System.out.println(CommonState.getTime()+" node is down");
    		return false;
    	} else {
    		return nd.getKademliaProtocol().getNode().addIncomingConnection(n,topic);
    	}
    		
    }
    
    
    public boolean isEclipsed() {
      
        if (getOutgoingConnections().size() == 0)
            return false;

        for (KademliaNode outConn : getOutgoingConnections())
            if (!outConn.is_evil)
                return false;

        return true;
    }
    
    public boolean addIncomingConnection(KademliaNode node) {
    	/*System.out.println(CommonState.getTime()+" "+incomingConnections.size()+" "+maxIncomingConnections);
    	for(KademliaNode n: incomingConnections)
    		System.out.println(CommonState.getTime()+" "+n.getId());*/
    	//if(incomingConnections.size()==maxIncomingConnections)System.out.println(CommonState.getTime()+" node full");
    	
    	if(incomingConnections.size()>=maxIncomingConnections) {
    		//System.out.println(CommonState.getTime()+" incoming connections full");
    		return false;
    	} else if (incomingConnections.contains(node)) {
    		//System.out.println(CommonState.getTime()+" incoming connection already existing");
    		return false;
    	}
    	if(incomingConnections.size()<maxIncomingConnections&&!incomingConnections.contains(node)) {
    		incomingConnections.add(node);
    		return true;
    	} else
    		return false;
    }		
    	
    public boolean addOutgoingConnection(KademliaNode node) {
    	if(outgoingConnections.size()<maxOutgoingConnections&&!outgoingConnections.contains(node)) {
    		outgoingConnections.add(node);
    		return true;
    	} else
    		return false;
    }
    
    public boolean isEmpty() {
    	return this.lookupResultBuffer.isEmpty();
    }
    
    
	public void sendLookup(Node n) {
		EDSimulator.add(0,generateTopicLookupMessage(topic),n, n.getKademliaProtocol().getProtocolID());
		setRequested(true);
	}
	// ______________________________________________________________________________________________
	/**
	 * generates a topic lookup message, by selecting randomly the destination and one of previousely registered topic.
	 * 
	 * @return Message
	 */
	protected Message generateTopicLookupMessage(String topic) {
		//System.out.println("New lookup message "+topic);

		Topic t = new Topic(topic);
		Message m = new Message(Message.MSG_INIT_TOPIC_LOOKUP, t);
		m.timestamp = CommonState.getTime();

		return m;
	}
}