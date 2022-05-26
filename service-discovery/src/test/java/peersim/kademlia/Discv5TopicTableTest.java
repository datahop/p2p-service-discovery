package peersim.kademlia;

import peersim.config.Configuration;
import peersim.config.ParsedProperties;
import peersim.core.CommonState;

public class Discv5TopicTableTest {

  protected static void setUpBeforeClass() {
    String[] array = new String[] {"config/simple.cfg"};
    Configuration.setConfig(new ParsedProperties(array));
    CommonState.setEndTime(Long.parseLong("100"));
    CommonState.setTime(Long.parseLong("0"));
  }

  // this table is not used anymore
  /*@Test
  public void ticketWaitingTimes() {
  	return;
      Discv5TicketTopicTable table = new Discv5TicketTopicTable();
      UniformRandomGenerator urg = new UniformRandomGenerator(KademliaCommonConfig.BITS, 1);
      table.setCapacity(10);
      table.setAdsPerQueue(1);
      table.setAdLifeTime(20);

      long rtt_delay = 1;
      long curr_time = 0;
      Topic topic = new Topic(new BigInteger("0"), "topic"+0);
      Ticket successful_ticket = null;
      Ticket failed_ticket = null;
      for(int i = 0; i < 20; i++) {
          System.out.println("Current time: " + curr_time);
          if (i>0 && i%2 ==0) {
              System.out.println("Making decision for topic: " + topic);
              Ticket [] tickets = table.makeRegisterDecision(curr_time);
              for (Ticket t:tickets) {
                  if (t.isRegistrationComplete()) {
                      successful_ticket = t;
                      System.out.println("Successful ticket for topic: " + t.getTopic() + " waiting time: " + t.getWaitTime());
                  }
                  else {
                      failed_ticket = t;
                      System.out.println("Failed ticket for topic: " + t.getTopic() + " waiting time: " + t.getWaitTime());
                  }
              }
              //assert(successful_ticket.getRegTime() < failed_ticket.getRegTime());
          }
          if (i%2 == 0) {
              topic = new Topic(new BigInteger("0"), "topic"+i);
          }
          System.out.println("Ticketing for topic: " + topic);
          KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
          Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
          System.out.println("Waiting time: " + ticket.getWaitTime());
          assert(ticket.getWaitTime() == 0);
          table.register_ticket(ticket, null, curr_time);
          curr_time += 1;
      }

      //Full table
      for(int i = 0; i < 10; i++) {
          System.out.println("Current time: " + curr_time);
          if (i>0 && i%2 ==0) {
              System.out.println("Making decision for topic: " + topic);
              Ticket [] tickets = table.makeRegisterDecision(curr_time);
              for (Ticket t:tickets) {
                  if (t.isRegistrationComplete()) {
                      successful_ticket = t;
                      System.out.println("Successful ticket for topic: " + t.getTopic() + " waiting time: " + t.getWaitTime());
                  }
                  else {
                      failed_ticket = t;
                      System.out.println("Failed ticket for topic: " + t.getTopic() + " waiting time: " + t.getWaitTime());
                  }
              }
              //assert(successful_ticket.getRegTime() < failed_ticket.getRegTime());
          }
          if (i%2 == 0) {
              topic = new Topic(new BigInteger("0"), "topic"+i);
          }
          System.out.println("Ticketing for topic: " + topic);
          KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
          Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
          System.out.println("Waiting time: " + ticket.getWaitTime());
          //assert(ticket.getWaitTime() == 0);
          table.register_ticket(ticket, null, curr_time);
          curr_time += 1;
      }
  }*/
}
