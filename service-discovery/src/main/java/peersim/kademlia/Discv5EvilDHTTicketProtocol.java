package peersim.kademlia;

/** Discv5 Ticket Evil Protocol implementation. */
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import peersim.config.Configuration;
import peersim.core.CommonState;
import peersim.core.Network;
import peersim.core.Node;
import peersim.edsim.EDSimulator;
import peersim.kademlia.operations.RegisterOperation;
import peersim.transport.UnreliableTransport;

public class Discv5EvilDHTTicketProtocol extends Discv5DHTTicketProtocol {

  // VARIABLE PARAMETERS
  final String PAR_ATTACK_TYPE = "attackType";
  final String PAR_NUMBER_OF_REGISTRATIONS = "numberOfRegistrations";
  final String PAR_REFRESH_TIME = "refreshTime";

  // type of attack (TopicSpam)
  private String attackType;
  // number of registrations to make
  private int numOfRegistrations;
  private int targetNumOfRegistrations;
  private boolean first = true;
  private HashMap<Topic, ArrayList<TopicRegistration>> evilTopicTable;
  private RoutingTable evilRoutingTable; // routing table only containing evil neighbors
  private HashMap<Topic, HashMap<BigInteger, Long>> initTicketRequestTime;
  private HashMap<Topic, HashMap<BigInteger, Long>> previousTicketRequestTime;

  private HashMap<String, List<BigInteger>> allSeen;

  private int n_regs;

  private int refreshTime;

  /**
   * Replicate this object by returning an identical copy.<br>
   * It is called by the initializer and do not fill any particular field.
   *
   * @return Object
   */
  public Object clone() {
    Discv5EvilDHTTicketProtocol dolly =
        new Discv5EvilDHTTicketProtocol(Discv5EvilDHTTicketProtocol.prefix);
    return dolly;
  }

  /**
   * Used only by the initializer when creating the prototype. Every other instance call CLONE to
   * create the new object.
   *
   * @param prefix String
   */
  public Discv5EvilDHTTicketProtocol(String prefix) {
    super(prefix);
    this.allSeen = new HashMap<>();
    this.n_regs = Configuration.getInt(prefix + "." + PAR_N, KademliaCommonConfig.N);
    this.refreshTime = Configuration.getInt(prefix + "." + PAR_REFRESH_TIME, 60000);

    this.attackType = Configuration.getString(prefix + "." + PAR_ATTACK_TYPE);
    this.numOfRegistrations = 0;
    this.targetNumOfRegistrations =
        Configuration.getInt(prefix + "." + PAR_NUMBER_OF_REGISTRATIONS, 0);
    this.evilTopicTable = new HashMap<Topic, ArrayList<TopicRegistration>>();
    this.evilRoutingTable =
        new RoutingTable(
            KademliaCommonConfig.NBUCKETS,
            KademliaCommonConfig.K,
            KademliaCommonConfig.MAXREPLACEMENT);
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

    } else {
      System.out.println("Invalid attacker type");
      System.exit(1);
    }
  }

  /**
   * This procedure is called only once and allow to inizialize the internal state of
   * KademliaProtocol. Every node shares the same configuration, so it is sufficient to call this
   * routine once.
   */
  protected void _init() {
    // execute once
    if (_ALREADY_INSTALLED) return;

    super._init();
  }

  /**
   * Start a register topic operation.<br>
   * If this is an on-going register operation with a previously obtained ticket, then send a
   * REGTOPIC message; otherwise, Find the ALPHA closest node and send REGTOPIC message to them
   *
   * @param m Message received (contains the node to find)
   * @param myPid the sender Pid
   */
  protected void handleInitRegister(Message m, int myPid) {
    Topic t = (Topic) m.body;

    logger.warning(
        "In handleInitRegister of EVIL "
            + t.getTopic()
            + " "
            + t.getTopicID()
            + " "
            + n_regs
            + " "
            + refreshTime);

    allSeen.put(t.getTopic(), new ArrayList<BigInteger>());

    if (this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_DOS)) {
      // if only a spammer than follow the normal protocol
      // super.handleInitRegisterTopic(m, myPid);
      return;
    }
    if (this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
      HashMap<BigInteger, Long> init = new HashMap<BigInteger, Long>();
      initTicketRequestTime.put(t, init);
      // logger.warning("Log"+initTicketRequestTime.get(t).ge);
      previousTicketRequestTime.put(t, new HashMap<BigInteger, Long>());

      // super.handleInitRegisterTopic(m, myPid);
    }
    if (first
        && (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_HYBRID)
            || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_MALICIOUS_REGISTRAR))) {
      first = false;
      logger.warning("Filling up the topic table with malicious entries");
      for (int i = 0; i < Network.size(); i++) {
        Node n = Network.get(i);
        KademliaProtocol prot = (KademliaProtocol) n.getKademliaProtocol();
        if (this.getNode().equals(prot.getNode())) continue; // skip this node
        if (prot.getNode().is_evil) { // add a registration to evilTopicTable
          TopicRegistration reg = new TopicRegistration(prot.getNode());
          Topic targetTopic = prot.getTargetTopic();
          ArrayList<TopicRegistration> regList = this.evilTopicTable.get(targetTopic);
          if (regList != null) regList.add(reg);
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
      if (this.getNode().equals(prot.getNode())) continue;
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

  protected void startRegistration(RegisterOperation rop, int myPid) {

    // int distToTopic = Util.logDistance((BigInteger) rop.getTopic().getTopicID(),
    // this.node.getId());
    // BigInteger[]  neighbours = this.routingTable.getNeighbours(distToTopic);

    /*for (BigInteger id : rop.getNeighboursList()) {
    	logger.warning("start reg neighbour "+id+" "+Util.logDistance(rop.getTopic().getTopicID(), id));
    }*/
    /*if(neighbours.length < KademliaCommonConfig.ALPHA)
    neighbours = this.routingTable.getKClosestNeighbours(KademliaCommonConfig.ALPHA, distToTopic);*/

    // rop.elaborateResponse(neighbours);
    // rop.available_requests = KademliaCommonConfig.ALPHA;

    // logger.warning("Start registration2 "+rop.getMessage().type+" "+rop.operationId+"
    // "+rop.getNeighboursList().size());
    Message message = rop.getMessage();
    message.operationId = rop.operationId;
    message.type = Message.MSG_REGISTER;
    message.src = this.node;

    List<BigInteger> registrars = allSeen.get(rop.getTopic().getTopic());

    logger.warning("Registrars " + registrars.size() + " " + n_regs);

    allSeen.remove(rop.getTopic().getTopic());

    rop.available_requests = KademliaCommonConfig.ALPHA;
    // send ALPHA messages

    int regs = registrars.size() > n_regs ? n_regs : registrars.size();

    for (int i = 0; i < regs; i++) {
      // BigInteger nextNode = rop.getNeighbour();
      // logger.warning("Nextnode "+nextNode);
      BigInteger nextNode = registrars.get(i);
      if (nextNode != null) {
        sendTicketRequest(nextNode, rop.topic, myPid);
      } else {
        break; // nextNode may be null, if the node has less than ALPHA neighbours
      }
    }
  }

  /**
   * Process a topic query message.<br>
   * The body should contain a topic. Return a response message containing the registrations for the
   * topic and the neighbors close to the topic.
   *
   * @param m Message received (contains the node to find)
   * @param myPid the sender Pid
   */
  protected void handleTopicQuery(Message m, int myPid) {

    Topic t = (Topic) m.body;
    TopicRegistration[] registrations = new TopicRegistration[0];

    if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)
        || this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_DOS)
        || this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
      // if only a spammer than follow the normal protocol
      super.handleTopicQuery(m, myPid);
    } else {
      ArrayList<TopicRegistration> regList = this.evilTopicTable.get(t);
      if (regList != null && !regList.isEmpty()) {
        registrations =
            (TopicRegistration[]) regList.toArray(new TopicRegistration[regList.size()]);
      }

      int result_len =
          KademliaCommonConfig.K > registrations.length
              ? registrations.length
              : KademliaCommonConfig.K;
      TopicRegistration[] final_results = new TopicRegistration[result_len];

      for (int i = 0; i < result_len; i++)
        final_results[i] = registrations[CommonState.r.nextInt(registrations.length)];

      BigInteger[] neighbours =
          this.evilRoutingTable.getNeighbours(Util.logDistance(t.getTopicID(), this.node.getId()));

      /*Message.TopicLookupBody body = new Message.TopicLookupBody(final_results, neighbours);
      Message response  = new Message(Message.MSG_TOPIC_QUERY_REPLY, body);
      response.operationId = m.operationId;
      response.src = this.node;
      response.ackId = m.id;
      logger.warning(" responds with Malicious TOPIC_QUERY_REPLY");
      sendMessage(response, m.src.getId(), myPid);*/

      Message.TopicLookupBody body = new Message.TopicLookupBody(registrations, neighbours);
      Message response = new Message(Message.MSG_TOPIC_QUERY_REPLY, body);
      response.operationId = m.operationId;
      response.src = this.node;
      assert m.src != null;
      response.dest = m.src;
      response.ackId = m.id;
      logger.info(" responds with TOPIC_QUERY_REPLY");
      sendMessage(response, m.src.getId(), myPid);
    }
  }

  protected void handleResponse(Message m, int myPid) {

    BigInteger[] neighbours = (BigInteger[]) m.body;
    for (String t : allSeen.keySet())
      if (allSeen.get(t) != null) allSeen.get(t).addAll(Arrays.asList(neighbours));

    logger.warning("handleresponse " + neighbours.length);

    super.handleResponse(m, myPid);
  }

  /**
   * Process a ticket request by malicious node. The goal here is to approve all registrations
   * immediately.
   */
  protected void handleTicketRequest(Message m, int myPid) {

    logger.warning("Handle ticket request EVIL");
    if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)
        || this.attackType.endsWith(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
      super.handleTicketRequest(m, myPid);
      return;
    }

    long curr_time = CommonState.getTime();
    // System.out.println("Ticket request received from " + m.src.getId()+" in node
    // "+this.node.getId());
    Topic topic = (Topic) m.body;

    KademliaNode advertiser = m.src;
    // System.out.println("TicketRequest handle "+topic.getTopic());
    transport = (UnreliableTransport) (Network.prototype).getProtocol(tid);
    long rtt_delay =
        2
            * transport.getLatency(
                Util.nodeIdtoNode(m.src.getId()), Util.nodeIdtoNode(m.dest.getId()));
    Ticket ticket =
        ((Discv5GlobalTopicTable) this.topicTable)
            .getTicket(topic, advertiser, rtt_delay, curr_time);
    // Send a response message with a ticket back to advertiser
    BigInteger[] neighbours =
        this.evilRoutingTable.getNeighbours(
            Util.logDistance(topic.getTopicID(), this.node.getId()));
    // BigInteger[] neighbours =
    // this.routingTable.getNeighbours(Util.logDistance(topic.getTopicID(), this.node.getId()));

    Message.TicketReplyBody body = new Message.TicketReplyBody(ticket, neighbours);

    if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_DOS)) {
      body =
          new Message.TicketReplyBody(
              new Ticket(topic, curr_time, 100000000, advertiser, rtt_delay, 0), new BigInteger[0]);
    }
    Message response = new Message(Message.MSG_TICKET_RESPONSE, body);

    // Message response = new Message(Message.MSG_TICKET_RESPONSE, ticket);
    response.ackId = m.id; // set ACK number
    response.operationId = m.operationId;
    response.src = this.node;
    assert m.src != null;
    response.dest = m.src;
    sendMessage(response, m.src.getId(), myPid);

    /*long curr_time = CommonState.getTime();
          Topic topic = (Topic) m.body;
          KademliaNode advertiser = new KademliaNode(m.src);
    transport = (UnreliableTransport) (Network.prototype).getProtocol(tid);
          long rtt_delay = 2*transport.getLatency(Util.nodeIdtoNode(m.src.getId()), Util.nodeIdtoNode(m.dest.getId()));
          // Generate a ticket without any waiting time
          Ticket ticket = new Ticket(topic, curr_time, 0, advertiser, rtt_delay);
          ticket.setMsg(m);

          // Send a response message with a ticket back to advertiser
    BigInteger[] neighbours = this.evilRoutingTable.getNeighbours(Util.logDistance(topic.getTopicID(), this.node.getId()));

      	Message.TicketRequestBody body = new Message.TicketRequestBody(ticket, neighbours);
    Message response  = new Message(Message.MSG_TICKET_RESPONSE, body);

          //Message response = new Message(Message.MSG_TICKET_RESPONSE, ticket);
    response.ackId = m.id; // set ACK number
    response.operationId = m.operationId;

          sendMessage(response, m.src.getId(), myPid);*/
  }

  /**
   * Process a register response message.<br>
   * The body should contain a ticket, which indicates whether registration is complete. In case it
   * is not, schedule sending a new register request
   *
   * @param m Message received (contains the node to find)
   * @param myPid the sender Pid
   */
  protected void handleRegisterResponse(Message m, int myPid) {

    Ticket ticket = (Ticket) m.body;

    Topic t = ticket.getTopic();

    if (!ticket.isRegistrationComplete()) {
      logger.warning(
          "Unsuccessful Registration of topic: "
              + ticket.getTopic().getTopic()
              + " at node: "
              + m.src.getId()
              + " wait time: "
              + ticket.getWaitTime()
              + " "
              + ticket.getCumWaitTime());
      Message register = new Message(Message.MSG_REGISTER, ticket);
      register.operationId = m.operationId;
      register.body = m.body;

      BackoffService backoff = registrationFailed.get(ticket);
      if (backoff == null) {
        backoff =
            new BackoffService(
                KademliaCommonConfig.AD_LIFE_TIME, KademliaCommonConfig.MAX_REGISTRATION_RETRIES);
        backoff.registrationFailed();
        registrationFailed.put(ticket, backoff);
      } else {
        backoff.registrationFailed();
      }
      logger.info(
          "Registration failed "
              + backoff.getTimesFailed()
              + " backing off "
              + +backoff.getTimeToWait()
              + " "
              + backoff.shouldRetry()
              + " "
              + ticket.getWaitTime());

      if ((backoff.shouldRetry() && ticket.getWaitTime() >= 0)
          && (ticket.getCumWaitTime() <= KademliaCommonConfig.REG_TIMEOUT)) {
        scheduleSendMessage(register, m.src.getId(), myPid, ticket.getWaitTime());
      } else {
        logger.warning(
            "Ticket request cumwaitingtime too big "
                + ticket.getCumWaitTime()
                + " or too many tries "
                + backoff.getTimesFailed());
        // ticketTables.get(topic.getTopicID()).removeRegisteredList(m.src.getId());
        RetryTimeout timeout = new RetryTimeout(ticket.getTopic(), m.src.getId());
        EDSimulator.add(
            KademliaCommonConfig.AD_LIFE_TIME,
            timeout,
            Util.nodeIdtoNode(this.node.getId()),
            myPid);

        if (ticket.getCumWaitTime() > KademliaCommonConfig.REG_TIMEOUT)
          KademliaObserver.reportOverThresholdWaitingTime(
              t.getTopic(), this.node.getId(), m.src.getId(), ticket.getWaitTime());
      }

    } else {
      logger.warning(
          "Registration succesful for topic "
              + ticket.getTopic().topic
              + " at node "
              + m.src.getId()
              + " at dist "
              + Util.logDistance(m.src.getId(), ticket.getTopic().getTopicID())
              + " "
              + ticket.getCumWaitTime());
      KademliaObserver.addAcceptedRegistration(
          t, this.node.getId(), m.src.getId(), ticket.getCumWaitTime());
      KademliaObserver.reportActiveRegistration(ticket.getTopic(), this.node.is_evil);

      if (this.nRefresh == 1) {

        if (scheduled.get(t.getTopic()) != null) {
          int sch = scheduled.get(t.getTopic()) + 1;
          scheduled.put(t.getTopic(), sch);
        } else {
          scheduled.put(t.getTopic(), 1);
        }
      }
      // Timeout to report expired ad (i.e., upon expiration of this successful registration)
      Timeout timeout = new Timeout(ticket.getTopic(), m.src.getId());
      EDSimulator.add(refreshTime, timeout, Util.nodeIdtoNode(this.node.getId()), myPid);
    }

    operations.remove(m.operationId);
  }

  /**
   * Response to a route request.<br>
   * Respond with only K-closest malicious peers
   *
   * @param m Message
   * @param myPid the sender Pid
   */
  protected void handleFind(Message m, int myPid, int dist) {

    if (this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_TOPIC_SPAM)
        || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_DOS)
        || this.attackType.equals(KademliaCommonConfig.ATTACK_TYPE_WAITING_TIME_SPAM)) {
      super.handleFind(m, myPid, dist);
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
    // response.body = m.body;
    response.src = this.node;
    response.dest = m.src;
    response.ackId = m.id; // set ACK number

    // send back the neighbours to the source of the message
    sendMessage(response, m.src.getId(), myPid);
  }

  /**
   * manage the peersim receiving of the events
   *
   * @param myNode Node
   * @param myPid int
   * @param event Object
   */
  public void processEvent(Node myNode, int myPid, Object event) {

    // super.processEvent(myNode, myPid, event);
    Message m;

    SimpleEvent s = (SimpleEvent) event;
    if (s instanceof Message) {
      m = (Message) event;
      m.dest = this.node;
    }

    // TODO we could simply let these "handle" calls made in the parent class
    switch (((SimpleEvent) event).getType()) {
      case Message.MSG_INIT_REGISTER:
        m = (Message) event;
        handleInitRegister(m, myPid);
        break;

      case Message.MSG_TOPIC_QUERY:
        m = (Message) event;
        handleTopicQuery(m, myPid);
        break;

      default:
        super.processEvent(myNode, myPid, event);
    }
  }
}
