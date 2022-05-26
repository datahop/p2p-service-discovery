package peersim.kademlia;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import org.junit.jupiter.api.Test;
import peersim.config.Configuration;
import peersim.config.ParsedProperties;
import peersim.core.CommonState;

public class Discv5GlobalTopicTableSameIpTest {

  protected static void setUpBeforeClass() {
    String[] array = new String[] {"config/simple.cfg"};
    Configuration.setConfig(new ParsedProperties(array));
    CommonState.setEndTime(Long.parseLong("100"));
    CommonState.setTime(Long.parseLong("0"));
  }

  @Test
  public void ticketWaitingTimes() {
    Discv5TicketTopicTable table = new Discv5GlobalTopicTable();
    UniformRandomGenerator urg = new UniformRandomGenerator(KademliaCommonConfig.BITS, 1);
    table.setCapacity(200);
    table.setAdLifeTime(300000);

    long rtt_delay = 1;
    long curr_time = 0;
    long totalTime = 1000000;
    Ticket successful_ticket = null;
    Ticket failed_ticket = null;
    // Register 2 topic0 at times 0 and 1, then make decision at 2;
    //  register 2 topic2 at times 2 and 3, then make decision at 4
    //  ...

    int[] topicRate = new int[] {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

    // Ticket [] tickets = table.makeRegisterDecision(curr_time);

    List<Ticket> pendingTickets = new ArrayList<Ticket>();
    HashMap<Ticket, Long> failedTimes = new HashMap<Ticket, Long>();

    int[] occupancy = new int[topicRate.length];
    while (curr_time < totalTime) {
      int topicnum = 1;
      if (curr_time % 10000 == 0) {
        for (int i : topicRate) {
          for (int j = 0; j < i; j++) {
            Topic topic = new Topic(new BigInteger("0"), "topic" + topicnum);
            // System.out.println("At: " + curr_time + " ticketing for topic: " + topic.getTopic());
            KademliaNode advertiser = new KademliaNode(urg.generate(), "127.0.0.1", 0);
            Ticket ticket = table.getTicket(topic, advertiser, rtt_delay, curr_time);
            // System.out.println("At: " + curr_time + " waiting time: " + ticket.getWaitTime());
            // assert(ticket.getWaitTime() == 0);
            table.register_ticket(ticket, null, curr_time);
          }
          topicnum++;
        }
      }
      curr_time += 1000;
      for (Ticket ticket : pendingTickets) {
        // System.out.println("Ticket wait time "+ticket.getWaitTime());
        if (failedTimes.get(ticket) != null)
          if (curr_time >= failedTimes.get(ticket) + ticket.getWaitTime())
            table.register_ticket(ticket, null, curr_time);
      }

      Ticket[] regTickets = table.makeRegisterDecision(curr_time);

      for (Ticket t : regTickets) {
        if (t.isRegistrationComplete()) {
          // System.out.println("At:" + curr_time + " successful registration for topic: " +
          // t.getTopic().getTopic()+" "+t.getCumWaitTime()+" "+t.getOccupancy());
          pendingTickets.remove(t);

          occupancy[
                  Integer.valueOf(
                          t.getTopic().getTopic().substring(5, t.getTopic().getTopic().length()))
                      - 1] =
              t.getOccupancy();
        } else {
          pendingTickets.remove(t);
          pendingTickets.add(t);
          failedTimes.put(t, curr_time);
          occupancy[
                  Integer.valueOf(
                          t.getTopic().getTopic().substring(5, t.getTopic().getTopic().length()))
                      - 1] =
              t.getOccupancy();
          // System.out.println("At:" + curr_time + " unsuccessful registration for topic: " +
          // t.getTopic().getTopic()+" "+t.getCumWaitTime()+" "+t.getOccupancy());

          // previousTime=curr_time;

        }
      }
    }

    int t = 1;
    for (int i : occupancy) {
      // System.out.println("Occupancy topic"+t+" "+i);
      t++;
    }

    int min = Arrays.stream(occupancy).min().getAsInt();
    int max = Arrays.stream(occupancy).max().getAsInt();

    // System.out.println("Min:"+min+" Max:"+max);//+" "+(double)max/min);

    // assert(min==0||max==0||!((double)max/min<1.5));

  }
}
