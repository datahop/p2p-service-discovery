package peersim.kademlia;

import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigInteger;
import java.util.Arrays;
import java.util.Random;
import org.apache.commons.math3.distribution.ZipfDistribution;
import peersim.config.Configuration;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;
import peersim.dynamics.NodeInitializer;

/**
 * This control initializes the whole network (that was already created by peersim) assigning a
 * unique NodeId, randomly generated, to every node.
 *
 * @author Daniele Furlan, Maurizio Bonani
 * @version 1.0
 */
public class CustomDistribution implements peersim.core.Control {

  private static final String PAR_PROT = "protocol";
  // The protocol run by malicious nodes
  private static final String PAR_EVIL_PROT = "evilProtocol";
  // Percentage of malicious nodes in the network
  private static final String PAR_PERCENT_EVIL = "percentEvilTopic";
  // Percentage of malicious nodes in the network
  private static final String PAR_PERCENT_EVIL_TOTAL = "percentEvil";
  // ID distribution of malicious nodes (uniform or nonuniform)
  private static final String PAR_ID_DIST = "idDistribution";
  // The topic ID attacked by malicious nodes (only in attack mode not in spam)
  private static final String PAR_ATTACK_TOPIC = "attackTopic";
  // The size of IP pool used by attackers
  private static final String PAR_IP_POOL_SIZE = "iPSize";
  // The size of ID pool used by attackers
  private static final String PAR_ID_POOL_SIZE = "nodeIdSize";
  // The mode of attack (topic spam or random spam)
  private static final String PAR_ATTACK_TYPE = "attackType";
  // Number of topics (used by honest nodes)
  private static final String PAR_TOPICNUM = "topicnum";
  // Zipf exponent to generate topic IDs in requsts by honest nodes
  private static final String PAR_ZIPF = "zipf";

  private static final String PAR_INIT = "init";

  private int protocolID;
  private int evilProtocolID;
  private double percentEvil;
  private double percentEvilTotal;
  private UniformRandomGenerator urg;
  private final int topicNum;
  private final double exp;
  private ZipfDistribution zipf;
  private String idDist;
  private int[] subtract;
  private int attackTopicNo;
  private String attackType;
  private int ipPoolSize;
  private int idPoolSize;

  protected NodeInitializer[] inits;

  public CustomDistribution(String prefix) {
    protocolID = Configuration.getPid(prefix + "." + PAR_PROT);
    // Optional configurations when including secondary (malicious) protocol:
    evilProtocolID = Configuration.getPid(prefix + "." + PAR_EVIL_PROT, -1);
    percentEvil = Configuration.getDouble(prefix + "." + PAR_PERCENT_EVIL, 0.0);
    percentEvilTotal = Configuration.getDouble(prefix + "." + PAR_PERCENT_EVIL_TOTAL, 0.0);
    topicNum = Configuration.getInt(prefix + "." + PAR_TOPICNUM, 1);
    exp = Configuration.getDouble(prefix + "." + PAR_ZIPF, -1);
    idDist =
        Configuration.getString(
            prefix + "." + PAR_ID_DIST, KademliaCommonConfig.UNIFORM_ID_DISTRIBUTION);
    attackTopicNo = Configuration.getInt(prefix + "." + PAR_ATTACK_TOPIC, -1);
    attackType =
        Configuration.getString(
            prefix + "." + PAR_ATTACK_TYPE, KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM);
    ipPoolSize = Configuration.getInt(prefix + "." + PAR_IP_POOL_SIZE, 0);
    idPoolSize = Configuration.getInt(prefix + "." + PAR_ID_POOL_SIZE, 0);

    Object[] tmp = Configuration.getInstanceArray(prefix + "." + PAR_INIT);
    inits = new NodeInitializer[tmp.length];

    if (exp != -1) zipf = new ZipfDistribution(topicNum, exp);
    urg = new UniformRandomGenerator(KademliaCommonConfig.BITS, CommonState.r);
    subtract = new int[this.topicNum];

    if (attackTopicNo != -1) {
      if (attackTopicNo > topicNum || topicNum < 1) {
        System.out.println("Invalid attackTopicNo parameter" + attackTopicNo);
        System.exit(1);
      }
    }
  }

  private BigInteger generate_id(String idDist, int topicNo, Topic t) {
    BigInteger id;

    if (idDist.equals(KademliaCommonConfig.NON_UNIFORM_ID_DISTRIBUTION)) {
      id = generate_non_uniform_id(topicNo, t);
      System.out.println(
          "Generated nonuniform id: "
              + id
              + " for topic "
              + t.getTopicID()
              + " "
              + Util.logDistance(t.getTopicID(), id));
    } else {
      id = urg.generate();
      System.out.println("Generated uniform id: " + id);
    }

    return id;
  }

  private BigInteger generate_non_uniform_id(int topicNo, Topic t) {

    int amountToSubstract = subtract[topicNo];
    subtract[topicNo] += 1;
    String str = String.valueOf(amountToSubstract);
    BigInteger b = new BigInteger(str);

    return t.getTopicID().subtract(b);
  }

  private String randomIpAddress(Random r) {
    String ipAddr =
        new String(
            r.nextInt(256) + "." + r.nextInt(256) + "." + r.nextInt(256) + "." + r.nextInt(256));

    return ipAddr;
  }

  /**
   * Scan over the nodes in the network and assign a randomly generated NodeId in the space
   * 0..2^BITS, where BITS is a parameter from the kademlia protocol (usually 160)
   *
   * <p>Assign a percentage of nodes (if percentEvil is greater than 0.0) to run a secondary
   * protocol - those nodes can be the malicious ones.
   *
   * @return boolean always false
   */
  public boolean execute() {

    Random r = new Random(5);
    int num_evil_nodes = (int) (Network.size() * percentEvilTotal);

    if (percentEvil > 0) {
      num_evil_nodes += calculateEvil(attackTopicNo, topicNum, exp) * percentEvil;
    }

    System.out.println("Number of evil nodes: " + num_evil_nodes);

    // ID pool used by Sybil nodes
    BigInteger[] idPool;
    idPool = new BigInteger[this.idPoolSize];
    for (int i = 0; i < idPoolSize; i++) {
      idPool[i] = urg.generate();
    }

    // IP pool used by Sybil nodes
    String[] ipPool;
    ipPool = new String[ipPoolSize];
    for (int i = 0; i < ipPoolSize; i++) {
      ipPool[i] = randomIpAddress(r);
    }

    for (int i = 0; i < Network.size(); ++i) {
      Node generalNode = Network.get(i);
      BigInteger id;
      BigInteger attackerID = null;
      KademliaNode node;
      String ip_address;
      /*if (i < num_evil_nodes) { // Evil node configuration
          int topicNo;

          // Set the topicNo
          if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_RANDOM_SPAM)) {
              topicNo = r.nextInt(Network.size()*Network.size()) + this.topicNum;
          }
          else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)||this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID)) {
              if (this.attackTopicNo != -1)
                  topicNo = this.attackTopicNo;
              else
                  topicNo = zipf.sample();
          }
          else {
              topicNo = zipf.sample();
          }
          String topic = new String("t"+topicNo);
          Topic t = new Topic(topic);

          // Set the node ID and attacker ID (latter is used to simulate Sybil nodes)
          if (this.idPoolSize > 0)  {
              attackerID = idPool[r.nextInt(idPoolSize)];
              System.out.println("Selected attacker ID from pool, id: " + attackerID);
          }
          else {
              attackerID = urg.generate();
              System.out.println("Generated attacker ID from pool, id: " + attackerID);
          }
          id = generate_id(idDist, topicNo, t);
          // Set the IP address
          if (this.ipPoolSize > 0)
          {
              ip_address = ipPool[r.nextInt(ipPoolSize)];
          }
          else {
              ip_address = randomIpAddress(r);
          }

          // Generate KademliaNode and set protocol
          node = new KademliaNode(id, attackerID, ip_address, 0);
          generalNode.setProtocol(protocolID, null);
          node.is_evil = true;
          ((KademliaProtocol) (Network.get(i).getProtocol(evilProtocolID))).setNode(node);
          generalNode.setKademliaProtocol((KademliaProtocol) (Network.get(i).getProtocol(evilProtocolID)));
          ((KademliaProtocol) (Network.get(i).getProtocol(evilProtocolID))).setProtocolID(evilProtocolID);
          //if (idDist.equals(KademliaCommonConfig.NON_UNIFORM_ID_DISTRIBUTION))
          ((KademliaProtocol) (Network.get(i).getProtocol(evilProtocolID))).setTargetTopic(t);
      }
      else { // Honest node configuration*/
      id = urg.generate();
      node = new KademliaNode(id, randomIpAddress(r), 0);
      // node = new KademliaNode(id, "0.0.0.0", 0);
      if (evilProtocolID != -1) {
        generalNode.setProtocol(evilProtocolID, null);
      }
      generalNode.setKademliaProtocol((KademliaProtocol) (Network.get(i).getProtocol(protocolID)));
      ((KademliaProtocol) (Network.get(i).getProtocol(protocolID))).setNode(node);
      ((KademliaProtocol) (Network.get(i).getProtocol(protocolID))).setProtocolID(protocolID);
      //  }
    }

    for (int i = 0; i < num_evil_nodes; i++) {

      // Add Node
      Node newNode = (Node) Network.prototype.clone();
      for (int j = 0; j < inits.length; ++j) inits[j].initialize(newNode);
      Network.add(newNode);
      BigInteger id;
      BigInteger attackerID = null;
      KademliaNode node;
      String ip_address;

      int topicNo;

      // Set the topicNo
      if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_RANDOM_SPAM)) {
        topicNo = r.nextInt(Network.size() * Network.size()) + this.topicNum;
      } else if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)
          || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID)) {
        if (this.attackTopicNo != -1) topicNo = this.attackTopicNo;
        else topicNo = zipf.sample();
      } else {
        topicNo = zipf.sample();
      }
      String topic = new String("t" + topicNo);
      Topic t = new Topic(topic);

      // Set the node ID and attacker ID (latter is used to simulate Sybil nodes)
      if (this.idPoolSize > 0) {
        attackerID = idPool[r.nextInt(idPoolSize)];
        System.out.println("Selected attacker ID from pool, id: " + attackerID);
      } else {
        attackerID = urg.generate();
        System.out.println("Generated attacker ID from pool, id: " + attackerID);
      }
      id = generate_id(idDist, topicNo, t);
      // Set the IP address
      if (this.ipPoolSize > 0) {
        ip_address = ipPool[r.nextInt(ipPoolSize)];
      } else {
        ip_address = randomIpAddress(r);
      }

      /*node = new KademliaNode(id, randomIpAddress(r), 0);
      //node = new KademliaNode(id, "0.0.0.0", 0);
      if (evilProtocolID != -1) {
      	newNode.setProtocol(evilProtocolID, null);
      }
      newNode.setKademliaProtocol((KademliaProtocol) (newNode.getProtocol(protocolID)));
      ((KademliaProtocol) (newNode.getProtocol(protocolID))).setNode(node);
      ((KademliaProtocol) (newNode.getProtocol(protocolID))).setProtocolID(protocolID);*/

      node = new KademliaNode(id, attackerID, ip_address, 0);
      newNode.setProtocol(protocolID, null);

      node.is_evil = true;
      ((KademliaProtocol) (newNode.getProtocol(evilProtocolID))).setNode(node);
      newNode.setKademliaProtocol((KademliaProtocol) (newNode.getProtocol(evilProtocolID)));
      ((KademliaProtocol) (newNode.getProtocol(evilProtocolID))).setProtocolID(evilProtocolID);
      // if (idDist.equals(KademliaCommonConfig.NON_UNIFORM_ID_DISTRIBUTION))
      ((KademliaProtocol) (newNode.getProtocol(evilProtocolID))).setTargetTopic(t);
      ((KademliaProtocol) (newNode.getProtocol(evilProtocolID)))
          .getNode()
          .setTopic(t.getTopic(), newNode);
    }

    return false;
  }

  private int calculateEvil(int targetTopic, int topicNum, double exp) {

    try {
      String filename =
          "./config/zipf/zipf_"
              + "exp_"
              + exp
              + "topics_"
              + topicNum
              + "size_"
              + Network.size()
              + ".csv";

      BufferedReader br = new BufferedReader(new FileReader(filename));

      String line = "";
      int i = 0;
      br.readLine(); // read header
      int counter = 0;
      while ((line = br.readLine()) != null) {
        String[] data = line.split(",");
        int nodeID = Integer.valueOf(data[0]);
        assert nodeID == i : "incorrect NodeID; should be " + i + " was " + nodeID;

        // convert to Integer to make sure the format is correct
        int topic = Integer.valueOf(data[1]);
        if (topic == targetTopic) counter++;
        i++;
      }
      br.close();
      return counter;
    } catch (FileNotFoundException e) {
      System.out.println(e);
      ZipfDistribution zipf = new ZipfDistribution(topicNum, exp);

      Integer[] topicsCounts = new Integer[topicNum];
      Arrays.fill(topicsCounts, Integer.valueOf(0));

      // int targetNodes = 0;
      // int count=0;
      for (int i = 0; i < Network.size(); ++i) {
        int topicIndex = zipf.sample() - 1;
        topicsCounts[topicIndex]++;
      }

      return topicsCounts[targetTopic];
    } catch (NumberFormatException e) {
      System.err.println("Incorrect conversion from node ID or topic number");
      e.printStackTrace();
    } catch (IOException e) {
      System.err.println("Error reading the input file");
      e.printStackTrace();
    }

    return 0;
  }
}
