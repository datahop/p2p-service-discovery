package peersim.kademlia;

import java.util.Comparator;
import peersim.config.Configuration;
import peersim.core.CommonState;
import peersim.core.Control;
import peersim.core.Network;
import peersim.core.Node;
import peersim.dynamics.NodeInitializer;
import peersim.edsim.EDSimulator;

/**
 * Turbulcen class is only for test/statistical purpose. This Control execute a node add or remove
 * (failure) with a given probability.<br>
 * The probabilities are configurabily from the parameters p_idle, p_add, p_rem.<br>
 * - p_idle (default = 0): probability that the current execution does nothing (i.e. no adding and
 * no failures).<br>
 * - p_add (default = 0.5): probability that a new node is added in this execution.<br>
 * - p_rem (deafult = 0.5): probability that this execution will result in a failure of an existing
 * node.<br>
 * If the user desire to change one probability, all the probability value MUST be indicated in the
 * configuration file. <br>
 * Other parameters:<br>
 * - maxsize (default: infinite): max size of network. If this value is reached no more add
 * operation are performed.<br>
 * - minsize (default: 1): min size of network. If this value is reached no more remove operation
 * are performed.<br>
 *
 * @author Daniele Furlan, Maurizio Bonani
 * @version 1.0
 */
public class Turbulence implements Control {

  private static final String PAR_PROT = "protocol";
  private static final String PAR_TRANSPORT = "transport";
  private static final String PAR_INIT = "init";

  /** specify a minimum size for the network. by default there is no limit */
  private static final String PAR_MINSIZE = "minsize";

  /** specify a maximum size for the network.by default there is limit of 1 */
  private static final String PAR_MAXSIZE = "maxsize";

  /** idle probability */
  private static final String PAR_IDLE = "p_idle";

  /** probability to add a node (in non-idle execution) */
  private static final String PAR_ADD = "p_add";

  /**
   * probability to fail a node (in non-idle execution). Note: nodes will NOT be removed from the
   * network, but will be set as "DOWN", in order to let peersim exclude automatically the
   * delivering of events destinates to them
   */
  private static final String PAR_REM = "p_rem";

  /** node initializers to apply on the newly added nodes */
  protected NodeInitializer[] inits;

  private String prefix;
  protected int kademliaid;
  // private int discv5id=-1;
  private int transportid;
  private int maxsize;
  private int minsize;
  private double p_idle;
  private double p_add;
  private double p_rem;

  // ______________________________________________________________________________________________
  public Turbulence(String prefix) {
    this.prefix = prefix;
    kademliaid = Configuration.getPid(this.prefix + "." + PAR_PROT);

    transportid = Configuration.getPid(this.prefix + "." + PAR_TRANSPORT);
    /*if (Configuration.isValidProtocolName(prefix + "." + DISCV5_PAR_PROT)) {
    discv5id = Configuration.getPid(this.prefix + "." + DISCV5_PAR_PROT);
      }*/

    minsize = Configuration.getInt(this.prefix + "." + PAR_MINSIZE, 1);
    maxsize = Configuration.getInt(this.prefix + "." + PAR_MAXSIZE, Integer.MAX_VALUE);

    Object[] tmp = Configuration.getInstanceArray(prefix + "." + PAR_INIT);
    inits = new NodeInitializer[tmp.length];
    for (int i = 0; i < tmp.length; ++i) inits[i] = (NodeInitializer) tmp[i];

    // load probability from configuration file
    p_idle = Configuration.getDouble(this.prefix + "." + PAR_IDLE, 0); // idle default 0
    p_add = Configuration.getDouble(this.prefix + "." + PAR_ADD, 0.5); // add default 0.5
    p_rem = Configuration.getDouble(this.prefix + "." + PAR_REM, 0.5); // add default 0.5

    // check probability values
    if (p_idle < 0 || p_idle > 1) {
      System.err.println(
          "Wrong event probabilty in Turbulence class: the probability PAR_IDLE must be between 0 and 1");
    } else if (p_add < 0 || p_add > 1) {
      System.err.println(
          "Wrong event probabilty in Turbulence class: the probability PAR_ADD must be between 0 and 1");
    } else if (p_rem < 0 || p_rem > 1) {
      System.err.println(
          "Wrong event probabilty in Turbulence class: the probability PAR_REM must be between 0 and 1");
    } else if (p_idle + p_add + p_rem > 1) {
      System.err.println(
          "Wrong event probabilty in Turbulence class: the sum of PAR_IDLE, PAR_ADD and PAR_REM must be 1");
    }

    System.err.println(
        String.format(
            "Turbolence: [p_idle=%f] [p_add=%f] [(min,max)=(%d,%d)]",
            p_idle, p_add, maxsize, minsize));
  }

  @SuppressWarnings("unchecked")
  public void sortNet() {
    Network.sort(
        new Comparator() {
          // ______________________________________________________________________________________
          public int compare(Object o1, Object o2) {
            Node n1 = (Node) o1;
            Node n2 = (Node) o2;
            KademliaProtocol p1 = (KademliaProtocol) (n1.getProtocol(kademliaid));
            KademliaProtocol p2 = (KademliaProtocol) (n2.getProtocol(kademliaid));
            if (p1 == null || p2 == null) return 0;
            return Util.put0(p1.node.getId()).compareTo(Util.put0(p2.node.getId()));
          }

          // ______________________________________________________________________________________
          public boolean equals(Object obj) {
            return compare(this, obj) == 0;
          }
          // ______________________________________________________________________________________
        });
  }

  // ______________________________________________________________________________________________
  public boolean add() {

    // Add Node
    Node newNode = (Node) Network.prototype.clone();
    for (int j = 0; j < inits.length; ++j) inits[j].initialize(newNode);
    Network.add(newNode);

    int count = 0;
    for (int i = 0; i < Network.size(); ++i) if (Network.get(i).isUp()) count++;

    System.out.println("Adding node " + count);

    // get kademlia protocol of new node
    KademliaProtocol newKad = (KademliaProtocol) (newNode.getProtocol(kademliaid));
    newNode.setKademliaProtocol(newKad);
    newKad.setProtocolID(kademliaid);
    // newNode.setProtocol(kademliaid, newKad);
    // set node Id
    UniformRandomGenerator urg =
        new UniformRandomGenerator(KademliaCommonConfig.BITS, CommonState.r);
    KademliaNode node = new KademliaNode(urg.generate(), "127.0.0.1", 0);
    ((KademliaProtocol) (newNode.getProtocol(kademliaid))).setNode(node);

    // sort network
    sortNet();

    // select one random bootstrap node
    Node start;
    do {
      start = Network.get(CommonState.r.nextInt(Network.size()));
    } while ((start == null) || (!start.isUp()));

    // create auto-search message (search message with destination my own Id)
    Message m = Message.makeInitFindNode(newKad.getNode().getId());
    m.timestamp = CommonState.getTime();

    // perform initialization
    newKad.routingTable.addNeighbour(
        ((KademliaProtocol) (start.getProtocol(kademliaid))).node.getId());

    // start auto-search
    EDSimulator.add(0, m, newNode, kademliaid);

    // find another random node (this is to enrich the k-buckets)
    Message m1 = Message.makeInitFindNode(urg.generate());
    m1.timestamp = CommonState.getTime();

    return false;
  }

  // ______________________________________________________________________________________________
  public boolean rem() {
    // select one random node to remove
    // System.out.println("Turbulence rm");

    Node remove;
    do {
      remove = Network.get(CommonState.r.nextInt(Network.size()));
    } while (remove == null
        || !remove.isUp()
        || remove.getKademliaProtocol().getNode().is_evil
        || remove.getIndex() < minsize);

    System.out.println(
        "Turbulence remove node "
            + remove.getKademliaProtocol().getNode().getId()
            + " with index: "
            + remove.getIndex());
    // remove node (set its state to DOWN)
    remove.setFailState(Node.DEAD);

    //// FIXME We don't use connections anymore

    return false;
  }

  // ______________________________________________________________________________________________
  /**
   * generates a register message, by selecting randomly the destination.
   *
   * @return Message
   */
  protected Message generateRegisterMessage(String topic) {
    Topic t = new Topic(topic);
    Message m = Message.makeRegister(t);
    m.timestamp = CommonState.getTime();

    return m;
  }

  // ______________________________________________________________________________________________
  /**
   * generates a topic lookup message, by selecting randomly the destination and one of previousely
   * registered topic.
   *
   * @return Message
   */
  protected Message generateTopicLookupMessage(String topic) {
    // System.out.println("New lookup message "+topic);

    Topic t = new Topic(topic);
    Message m = new Message(Message.MSG_INIT_TOPIC_LOOKUP, t);
    m.timestamp = CommonState.getTime();

    return m;
  }

  // ______________________________________________________________________________________________
  /**
   * generates a random find node message, by selecting randomly the destination.
   *
   * @return Message
   */
  protected Message generateFindNodeMessage() {
    // existing active destination node
    Node n = Network.get(CommonState.r.nextInt(Network.size()));
    while (!n.isUp()) {
      n = Network.get(CommonState.r.nextInt(Network.size()));
    }

    Message m = Message.makeInitFindNode(n.getKademliaProtocol().getNode().getId());
    m.timestamp = CommonState.getTime();

    return m;
  }

  public void addRandomConnections(Node iNode, int num) {
    int sz = Network.size();

    KademliaProtocol iKad = iNode.getKademliaProtocol();

    for (int k = 0; k < num; k++) {
      int index = CommonState.r.nextInt(sz);
      KademliaProtocol jKad = Network.get(index).getKademliaProtocol();

      iKad.routingTable.addNeighbour(jKad.node.getId());
    }
  }

  public void addNearNodes(Node iNode, int num) {
    // add other 50 near nodes
    int sz = Network.size();
    KademliaProtocol iKad = (KademliaProtocol) (iNode.getKademliaProtocol());
    int i = iNode.getIndex();
    int start = i;
    if (i > sz - 50) {
      start = sz - 25;
    }
    for (int k = 0; k < 50; k++) {
      start = start++;
      if (start > 0 && start < sz) {
        KademliaProtocol jKad = (KademliaProtocol) (Network.get(start++).getKademliaProtocol());
        iKad.routingTable.addNeighbour(jKad.node.getId());
      }
    }
  }

  // ______________________________________________________________________________________________
  public boolean execute() {
    // throw the dice
    // System.out.println("Turbulence execute");
    // if(CommonState.getTime()<100000)
    //	return false;
    double dice = CommonState.r.nextDouble();
    if (dice < p_idle) return false;

    // get network size
    int sz = Network.size();
    for (int i = 0; i < Network.size(); i++) {
      if (!Network.get(i).isUp()) sz--;
    }
    // perform the correct operation basing on the probability
    if (dice < p_idle) {
      return false; // do nothing
    } else if (dice < (p_idle + p_add) && sz < maxsize) {
      return add();
    } else if (sz > minsize) {
      return rem();
    }

    return false;
  }
} // End of class
