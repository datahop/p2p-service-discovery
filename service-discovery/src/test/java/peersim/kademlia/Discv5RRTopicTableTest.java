package peersim.kademlia;

import peersim.config.Configuration;
import peersim.config.ParsedProperties;
import peersim.core.CommonState;

public class Discv5RRTopicTableTest {

  protected static void setUpBeforeClass() {
    String[] array = new String[] {"config/simple.cfg"};
    Configuration.setConfig(new ParsedProperties(array));
    CommonState.setEndTime(Long.parseLong("100"));
    CommonState.setTime(Long.parseLong("0"));
  }
  // this table is not used anymore
  /*@Test
  public void ticketWaitingTimes() {
      Discv5TicketTopicTable table = new Discv5RRTopicTable();
      UniformRandomGenerator urg = new UniformRandomGenerator(KademliaCommonConfig.BITS, 1);
      table.setCapacity(10);
      table.setAdsPerQueue(10);
      table.setAdLifeTime(20);

      long rtt_delay = 1;
      long curr_time = 0;
      Topic topic = new Topic(new BigInteger("0"), "topic"+0);
      Ticket successful_ticket = null;
      Ticket failed_ticket = null;
      // Register 2 topic0 at times 0 and 1, then make decision at 2;
      //  register 2 topic2 at times 2 and 3, then make decision at 4
      //  ...
      for(curr_time = 0; curr_time <= 10; curr_time++) {
          System.out.println("Current time: " + curr_time);
          if (curr_time>0 && curr_time%2 ==0) {
              System.out.println("At: " + curr_time + " making decision for topic: " + topic.getTopic());
              Ticket [] tickets = table.makeRegisterDecision(curr_time);
              for (Ticket t:tickets) {
                  if (t.isRegistrationComplete()) {
                      successful_ticket = t;
                      System.out.println("At:" + curr_time + " successful registration for topic: " + t.getTopic().getTopic());
                  }
                  else {
                      failed_ticket = t;
                      System.out.println("At: " + curr_time + " failed ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
                  }
              }
              //assert(successful_ticket.getRegTime() < failed_ticket.getRegTime());
          }
          if (curr_time%2 == 0) {
              topic = new Topic(new BigInteger("0"), "topic"+curr_time);
          }
          if (curr_time == 10)
              break;
          System.out.println("At: " + curr_time + " ticketing for topic: " + topic.getTopic());
          KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
          Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
          System.out.println("At: " + curr_time + " waiting time: " + ticket.getWaitTime());
          assert(ticket.getWaitTime() == 0);
          table.register_ticket(ticket, null, curr_time);
      }

      // Step 2
      // At this point (time = 10), the topic table is full and should contain
      // topics 0, 2, 4, 6, and 8 have each 2 registrations
      // Add ten more topics at time 10
      // These should be scheduled as round-robin
      boolean makeDecision = false;
      HashMap<Long, ArrayList<Ticket>> ticketDecisionTimes = new HashMap<Long, ArrayList<Ticket>>();
      for(curr_time=11 ; curr_time < 40; curr_time++) {
          System.out.println("At: " + curr_time);
          if (makeDecision) {
              makeDecision = false;
              Ticket [] tickets = table.makeRegisterDecision(curr_time);
              for (Ticket t:tickets) {
                  if (t.isRegistrationComplete()) {
                      successful_ticket = t;
                      System.out.println("At: " + curr_time + " successful registration for topic: " + t.getTopic().getTopic());
                  }
                  else {
                      System.out.println("At: " + curr_time + " failed ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
                      ArrayList<Ticket> scheduled_tickets = ticketDecisionTimes.get(t.getWaitTime() + curr_time);
                      if (scheduled_tickets == null)  {
                          scheduled_tickets = new ArrayList<Ticket>();
                          scheduled_tickets.add(t);
                          ticketDecisionTimes.put(t.getWaitTime() + curr_time, scheduled_tickets);
                      }
                      else
                          scheduled_tickets.add(t);
                      }
              }
          }

          if (curr_time%2 == 0) {
              long topicNumber = curr_time - 10;
              topic = new Topic(new BigInteger("0"), "topic"+topicNumber);
          }
          if (curr_time <= 20 ) {
              KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
              Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
              System.out.println("At: " + curr_time + " got ticket for topic: " + topic.getTopic() + " with waiting time: " + ticket.getWaitTime());
              if(ticket.getWaitTime() > 0) {

                  ArrayList<Ticket> tickets = ticketDecisionTimes.get(ticket.getWaitTime() + curr_time);
                  if (tickets == null)  {
                      tickets = new ArrayList<Ticket>();
                      tickets.add(ticket);
                      ticketDecisionTimes.put(ticket.getWaitTime() + curr_time, tickets);
                  }
                  else
                      tickets.add(ticket);
              }
          }
          //System.out.println("At: " + curr_time + " first make decision event will take place at: " + registrationTimes.getFirst());
          ArrayList<Ticket> ticketsToRegister = ticketDecisionTimes.get(curr_time);
          if ( ( ticketsToRegister != null ) && ( ticketsToRegister.size() > 0 ) ) {
              makeDecision = true;
              for (Ticket ticket : ticketsToRegister)  {
                  table.register_ticket(ticket, null, curr_time);
                  System.out.println("At: " + curr_time + " registering a ticket for topic: " + ticket.getTopic().getTopic());
              }
          }
      }*/
  /*
      Ticket [] tickets = null;
      for(int i = 0; i < 30; i++) {
          if (registrationTimes.size() > 0 && registrationTimes.getFirst() == curr_time) {
              table.register_ticket(ticket, null, curr_time);
              registrationTimes.pop();
          }
          tickets = table.makeRegisterDecision(curr_time);
          curr_time++;
          for (Ticket t:tickets) {
              if (t.isRegistrationComplete()) {
                  successful_ticket = t;
                  System.out.println("Successful ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
              }
              else {
                  failed_ticket = t;
                  System.out.println("Failed ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
              }
          }
      }


      // Step 3
      //Full table
      for(int i = 0; i < 10; i++) {
          System.out.println("Current time: " + curr_time);
          if (i>0 && i%2 ==0) {
              System.out.println("Making decision for topic: " + topic.getTopic());
              tickets = table.makeRegisterDecision(curr_time);
              for (Ticket t:tickets) {
                  if (t.isRegistrationComplete()) {
                      successful_ticket = t;
                      System.out.println("Successful ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
                  }
                  else {
                      failed_ticket = t;
                      System.out.println("Failed ticket for topic: " + t.getTopic().getTopic() + " waiting time: " + t.getWaitTime());
                  }
              }
              //assert(successful_ticket.getRegTime() < failed_ticket.getRegTime());
          }
          if (i%2 == 0) {
              topic = new Topic(new BigInteger("0"), "topic"+i);
          }
          System.out.println("Ticketing for topic: " + topic.getTopic());
          KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
          Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
          System.out.println("Waiting time: " + ticket.getWaitTime());
          //assert(ticket.getWaitTime() == 0);
          table.register_ticket(ticket, null, curr_time);
          curr_time += 1;
      }
  }*/
}
