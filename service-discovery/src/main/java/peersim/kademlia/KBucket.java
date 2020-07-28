package peersim.kademlia;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import java.util.TreeMap;

import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;

/**
 * This class implements a kademlia k-bucket. Function for the management of the neighbours update are also implemented
 * 
 * @author Daniele Furlan, Maurizio Bonani
 * @version 1.0
 */
public class KBucket implements Cloneable {

	// k-bucket array
	//protected TreeMap<BigInteger, Long> neighbours = null;
	protected List<BigInteger> neighbours;

	//replacementList
	//protected TreeMap<BigInteger, Long> replacements = null;
	protected List<BigInteger> replacements;

	protected RoutingTable rTable;
	//protected KademliaProtocol prot;
	// empty costructor
	public KBucket(RoutingTable rTable) {
		//neighbours = new TreeMap<BigInteger, Long>();
		//System.out.println("New bucket "+prot.kademliaid);
		//this.prot = prot;
		this.rTable = rTable;
		neighbours = new ArrayList<BigInteger>();
		replacements = new ArrayList<BigInteger>();
	}

	// add a neighbour to this k-bucket
	public void addNeighbour(BigInteger node) {
		//long time = CommonState.getTime();
		for(BigInteger n : neighbours) {
			if(n.compareTo(node)==0)return;
		}
		if (neighbours.size() < KademliaCommonConfig.K) { // k-bucket isn't full
			//neighbours.put(node, time); // add neighbour to the tail of the list
			neighbours.add(node);
			removeReplacement(node);
		} else {
			addReplacement(node);
		}
	}

	// add a replacement node in the list
	public void addReplacement(BigInteger node) {
		//long time = CommonState.getTime();
		
		for(BigInteger r : replacements) {
			if(r.compareTo(node)==0)return;
		}
		replacements.add(0,node);

		if (replacements.size() > KademliaCommonConfig.MAXREPLACEMENT) { // k-bucket isn't full
			//replacements.put(node, time); // add neighbour to the tail of the list
			replacements.remove(replacements.size()-1);
		} 
	}
	// remove a neighbour from this k-bucket
	public void removeNeighbour(BigInteger node) {
		neighbours.remove(node);
	}
	
	// remove a replacement node in the list
	public void removeReplacement(BigInteger node) {
		replacements.remove(node);
	}

	public Object clone() {
		KBucket dolly = new KBucket(rTable);
		for (BigInteger node : neighbours) {
			//System.out.println("clone kbucket");
			dolly.neighbours.add(new BigInteger(node.toByteArray()));
		}
		return dolly;
	}

	public String toString() {
		String res = "{\n";

		for (BigInteger node : neighbours) {
			res += node + "\n";
		}

		return res + "}";
	}
	
	public void checkAndReplaceLast(int kademliaid) {
		if (neighbours.size() == 0||CommonState.getTime()==0) 
			// Entry has moved, don't replace it.
			return;


		//System.out.println("Replace node "+neighbours.get(neighbours.size()-1)+" at  "+CommonState.getTime());

		Node node = Util.nodeIdtoNode(neighbours.get(neighbours.size()-1),kademliaid);
		//System.out.println("Replace node "+neighbours.get(neighbours.size()-1)+" at "+CommonState.getTime());
		KademliaProtocol remote = (KademliaProtocol) node.getProtocol(kademliaid);
		//((KademliaProtocol) Network.get(m).getProtocol(kademliaid)).node.getId();
		remote.routingTable.sendToFront(rTable.nodeId);
		
		//System.out.println("checkAndReplaceLast "+remote.getNode().getId()+" at "+CommonState.getTime()+" at "+rTable.nodeId);

		
		if(node.getFailState()!=Node.OK) {
			// Still the last entry.
			neighbours.remove(neighbours.size()-1);
			if(replacements.size()>0) {
				Random rand = new Random();
				BigInteger n = replacements.get(rand.nextInt(replacements.size()));
				neighbours.add(n);
				replacements.remove(n);
			}

		}
		
	}
	

}
