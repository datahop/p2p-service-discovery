package peersim.kademlia;

/**
 * Fixed Parameters of a kademlia network. They have a default value and can be configured at startup of the network, once only.
 * 
 * @author Daniele Furlan, Maurizio Bonani
 * @version 1.0
 */
public class KademliaCommonConfig {

	public static int BITS = 256; // length of Id (default is 160)

	public static int NBUCKETS = 256;
	public static int K = 16; // dimension of k-buckets (default is 5)
	public static int ALPHA = 3; // number of simultaneous lookup (default is 3)
	public static int TOPIC_TABLE_CAP = 10000; //the number of topics per node we can regiter
	public static int MAXREPLACEMENT = 10; //the number of nodes saved in the replacement list
	public static int REFRESHTIME = 10*100; //periodic time used to check nodes down in k-buckets
	public static int MAXCONNECTIONS = 50; //periodic time used to check nodes down in k-buckets
	public static int MAXFINDNODEFAILURES = 5; //periodic time used to check nodes down in k-buckets
    public static int ADS_PER_QUEUE = 200; //the number of ads per topic queue
    public static int AD_LIFE_TIME = 250000; //life time of ads the topic table
    public static int ONE_UNIT_OF_TIME = 1; // smallest time value
    public static int TOPIC_PEER_LIMIT = 50; //how many high quality nodes do we want to find for each topic; after this number we stop

    // Attack Types:
    public static String ATTACK_TYPE_TOPIC_SPAM = "TopicSpam";
    public static String ATTACK_TYPE_MALICIOUS_REGISTRAR = "MaliciousRegistrar";
    public static String ATTACK_TYPE_HYBRID = "HybridAttacker";
    //TODO show the distribution of nodes discovered (do everyone discover the same? Or different?)
    // Settings for CustomDistribution (id distribution setting for nodes)
    public static String NON_UNIFORM_ID_DISTRIBUTION = "nonUniform";
    public static String UNIFORM_ID_DISTRIBUTION = "uniform";
    
	/**
	 * short information about current mspastry configuration
	 * 
	 * @return String
	 */
	public static String info() {
		return String.format("[K=%d][ALPHA=%d][BITS=%d][TOPIC_TABLE_CAP=%d]", K, ALPHA, BITS, TOPIC_TABLE_CAP);
	}

}
