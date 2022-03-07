package peersim.kademlia;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.TreeMap;

import peersim.core.CommonState;

import java.util.Map;
//import java.util.Random;
import java.util.Set;
import peersim.kademlia.KademliaCommonConfig;

/**
 * Gives an implementation for the routing table component of a kademlia node
 * 
 * @author Daniele Furlan, Maurizio Bonani
 * @version 1.0
 */
public class RoutingTable implements Cloneable {

	protected int bucketMinDistance;

	// node ID of the node
	protected BigInteger nodeId = null;

	// k-buckets
	protected KBucket k_buckets[];

	protected int nBuckets,k,maxReplacements;
	
	//protected int maxAddresses = KademliaCommonConfig.MAX_ADDRESSES_TABLE;
	// ______________________________________________________________________________________________
	/**
	 * instanciates a new empty routing table with the specified size
	 */
	public RoutingTable(int nBuckets, int k, int maxReplacements) {
		k_buckets = new KBucket[nBuckets];
		this.nBuckets = nBuckets;
		this.k=k;
		this.maxReplacements=maxReplacements;
		bucketMinDistance = KademliaCommonConfig.BITS - nBuckets;
		for (int i = 0; i < k_buckets.length; i++) {
			k_buckets[i] = new KBucket(this,k,maxReplacements);
		}

	}

	public int containsNode(BigInteger id){
		for(int i = 0; i < nBuckets; i++){
			for(BigInteger nodeId: k_buckets[i].neighbours){
				if(nodeId.equals(id))
					return i;
			}
		}
		return -1;
	}
	
	public boolean compareAddresses(String addr) {

		for(int i = 0; i < nBuckets; i++){
			HashSet<String> addresses = k_buckets[i].getAddresses();
			if(addresses.contains(addr))return true;
		}
		return false;
	}

	// add a neighbour to the correct k-bucket
	public boolean addNeighbour(BigInteger node) {
		// get the lenght of the longest common prefix (correspond to the correct k-bucket)
		if(node.compareTo(nodeId)==0) return false;
		    
        KademliaNode kadNode = Util.nodeIdtoNode(node).getKademliaProtocol().getNode();
        // FIXME is the below check necessary?
	    if(compareAddresses(kadNode.getAddr()))
            return false;
            
        return getBucket(node).addNeighbour(node);
	}

	// remove a neighbour from the correct k-bucket
	public void removeNeighbour(BigInteger node) {

		getBucket(node).removeNeighbour(node);
	}
	
	// return neighbors 
	public BigInteger[] getNeighbours (final BigInteger dist) {

		BigInteger[] result = new BigInteger[0];
		ArrayList<BigInteger> resultList = new ArrayList<BigInteger>();
		resultList.addAll(bucketAtDistance(dist).neighbours);
        
        int bucket = getBucketIndexFromDistance(dist);
		if( (resultList.size() < k) && ( (bucket-1)>=0) ) {
			resultList.addAll(bucketAtDistance(bucket-1).neighbours);
			while(resultList.size()>k)
                resultList.remove(resultList.size()-1);
		}
        
		if( (resultList.size() < k) && ( (bucket + 1) < this.getNumBuckets()) ) {
			resultList.addAll(bucketAtDistance(bucket + 1).neighbours);
			while(resultList.size()>k)
                resultList.remove(resultList.size()-1);
		}

		return resultList.toArray(result);
	}
	
    // return neighbors 
	public BigInteger[] getNeighboursAtBucket (final int bucket) {

		BigInteger[] result = new BigInteger[0];
		ArrayList<BigInteger> resultList = new ArrayList<BigInteger>();
		resultList.addAll(k_buckets[bucket].neighbours);
        
		return resultList.toArray(result);
	}
	
    // return the closest neighbour to a key from the correct k-bucket
	public BigInteger[] getKClosestNeighbours(final BigInteger key, final BigInteger src) {
		// resulting neighbours
		BigInteger[] result = new BigInteger[k];
		ArrayList<BigInteger> resultList = new ArrayList<BigInteger>();

		// neighbour candidates
		ArrayList<BigInteger> neighbour_candidates = new ArrayList<BigInteger>();

		// return the k-bucket if is full
		if (bucketOfDestination(key).neighbours.size() >= k) {
			return bucketOfDestination(key).neighbours.toArray(result);
		}
		
        // else get k closest node from all k-buckets
		int bucket = getBucketIndexOfDestination(key);

		while (bucket >= 0) {
			neighbour_candidates.addAll(k_buckets[bucket].neighbours);
			bucket--;
		}
	    // remove source id
        neighbour_candidates.remove(src);

		// create a map (distance, node)
		TreeMap<BigInteger, BigInteger> distance_map = new TreeMap<BigInteger, BigInteger>();

		for (BigInteger node : neighbour_candidates) {
			distance_map.put(Util.distance(node, key), node);
		}

		int i = 0;
		for (BigInteger iii : distance_map.keySet()) {
			if (i < k) {
				result[i] = distance_map.get(iii);
				i++;
			}
		}

		return result;
	}
	
    /*
	public BigInteger[] getKClosestNeighbours (final int k, int dist) {
		BigInteger[] result = new BigInteger[k];
		ArrayList<BigInteger> resultList = new ArrayList<BigInteger>();
		while(resultList.size()<k && dist<=KademliaCommonConfig.BITS) {
			resultList.addAll(bucketAtDistance(dist).neighbours);
			dist++;
		}
		
		return resultList.toArray(result);

	}*/



	// ______________________________________________________________________________________________
	public Object clone() {
		RoutingTable dolly = new RoutingTable(nBuckets,k,maxReplacements);
		for (int i = 0; i < k_buckets.length; i++) {
			k_buckets[i] = new KBucket(this,k,maxReplacements);
		}

		return dolly;
	}

	// ______________________________________________________________________________________________
	/**
	 * print a string representation of the table
	 * 
	 * @return String
	 */
	public String toString() {
		return "";
	}
	
	/**
	 * Check nodes and replace buckets with valid nodes from replacement list
	 * 
	 */
	public void refreshBuckets() {

		KBucket b = k_buckets[CommonState.r.nextInt(nBuckets)];
		if(b.neighbours.size()>0) {
			b.checkAndReplaceLast();
			return;
		}

	}
	
	public Set<BigInteger> getAllNeighbours(){
		Set<BigInteger> allNeighbours = new HashSet<BigInteger>();
		for(KBucket b: k_buckets) {
			allNeighbours.addAll(b.neighbours);
		}
		return allNeighbours;
	}
	
	public void sendToFront(BigInteger node)
	{
		if(getBucket(node).neighbours.remove(node))
			getBucket(node).neighbours.add(0,node);
	}
	
	
	/**
	 * return the bucket for a given node
	 * 
	 * @param node
	 *            BigInteger 
	 *            
	 * @return KBucket
     *            
	 */
	public KBucket getBucket(BigInteger node) {

        return bucketAtDistance(Util.distance(nodeId, node));
	}

	/**
	 * return the KBucket for a given bucket index
	 * 
	 * @param bucketIndex
	 *            int 
	 *            
	 * @return KBucket
     *            
	 */
    public KBucket bucketFromIndex(int bucketIndex) {
        return k_buckets[bucketIndex];
    }

	/**
	 * return the bucket index from an integer bucket distance 
	 * 
	 * @param dist
	 *            an integer between 0 .. KademliaCommonConfig.BITS
	 *            
	 * @return bucket index   
     *            an integer from 0 .. getNumBuckets()-1
	 */
    public int getBucketIndexFromDistance(int dist) {

		if (dist <= bucketMinDistance) {
			return 0;
		}
		return dist - bucketMinDistance - 1;
    }
    
	/**
	 * return the bucket index from a BigInteger distance (output of Util.distance())
	 * 
	 * @param distance
	 *            a BigInteger (e.g., XOR output or log distance)
	 *            
	 * @return bucket index   
     *            an integer from 0 .. getNumBuckets()-1
	 */
    public int getBucketIndexFromDistance(BigInteger distance) {
        int dist;
        if (KademliaCommonConfig.DISTANCE_METRIC == KademliaCommonConfig.LOG_DISTANCE) {
		    dist = distance.intValue();
        }
        else { //XOR distance
            dist = Util.prefixLenFromXORDistance(distance);       
        }
        return getBucketIndexFromDistance(dist);
    }

	/**
	 * return the bucket index of a destination node
	 * 
	 * @param destintation
	 *            a destination node
	 *            
	 * @return bucket index   
     *            an integer from 0 to getNumBuckets()-1
	 */
	public int getBucketIndexOfDestination(BigInteger destination) {
        BigInteger distance = Util.distance(nodeId, destination);

        int bucketIndex = getBucketIndexFromDistance(distance);

        return bucketIndex;
	}
	
	/**
	 * return the KBucket at the given distance 
	 * 
	 * @param dist 
	 *            an int in the range 0 .. KademliaCommonConfig.BITS
	 *            
	 * @return KBucket 
     *            the KBucket for a given distance
	 */
    protected KBucket bucketAtDistance(int dist) {
		
		return k_buckets[getBucketIndexFromDistance(dist)];
    }
	
	/**
	 * return the KBucket at the given distance 
	 * 
	 * @param dist 
	 *            an int in the range 0 .. KademliaCommonConfig.BITS
	 *            
	 * @return KBucket 
     *            the KBucket for a given distance
	 */
	protected KBucket bucketAtDistance(BigInteger distance) {
        int bucketIndex = getBucketIndexFromDistance(distance);

		return k_buckets[bucketIndex]; 
	}

	/**
	 * return the KBucket of a destination
	 * 
	 * @param dest
	 *            BigInteger
	 *            
	 * @return KBucket 
     *            the KBucket of a given destination
	 */
    public KBucket bucketOfDestination(BigInteger dest) {
        int bucketIndex = getBucketIndexOfDestination(dest);

        return k_buckets[bucketIndex];
    }
	
	public void setNodeId(BigInteger id){
		this.nodeId = id;
	}
	
	public BigInteger getNodeId() {
		return this.nodeId;
	}
	protected BigInteger generateRandomNode(int b) {
		
		BigInteger randNode;

		UniformRandomGenerator urg = new UniformRandomGenerator(KademliaCommonConfig.BITS, CommonState.r);
		BigInteger rand = urg.generate();
		String rand2 = Util.put0(rand);
				
		int distance = b + this.bucketMinDistance + 1;
					
		int prefixlen = (KademliaCommonConfig.BITS - distance);
				
		String nodeId2 = Util.put0(nodeId);
				
		String randomString = "";

		if(prefixlen>0) {
			if(nodeId2.charAt(prefixlen)==rand2.charAt(prefixlen)) {
				if(Integer.parseInt(nodeId2.substring(prefixlen-1,prefixlen))==0) {
					randomString = nodeId2.substring(0,prefixlen).concat("1");
				} else {
					randomString = nodeId2.substring(0,prefixlen).concat("0");
				}
				randomString = randomString.concat(rand2.substring(prefixlen+1,rand2.length()));
			} else 
				randomString = nodeId2.substring(0,prefixlen).concat(rand2.substring(prefixlen,rand2.length()));
			
			randNode = new BigInteger(randomString,2);

		} else {
			randNode = rand;
		}
				
		return randNode;
	}
	
	public int getbucketMinDistance() {
		return bucketMinDistance;
	}

    public int getNumBuckets() {
        return nBuckets;
    }
	

	// ______________________________________________________________________________________________

} // End of class
// ______________________________________________________________________________________________
