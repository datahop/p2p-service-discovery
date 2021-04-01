package peersim.kademlia;

import java.util.Map;
import java.util.HashMap;
import java.util.SortedMap;
import java.util.TreeMap;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.logging.Logger;
import java.util.Collections;
import java.math.BigInteger;

import peersim.kademlia.Topic;
import peersim.kademlia.TopicRegistration;
import peersim.core.CommonState;

// Round-robin Discv5 Topic table
public class Discv5RRTopicTable extends Discv5TopicTable { // implements TopicTable 

    private SortedMap<Topic, Long> registrationTimes; 
    // index to the current topic in the round-robin
    boolean roundRobin;
    Long endOfRoundTime; //time of next round start
    Long startOfRoundTime; // time of current round start
    int nextTopicIndex; //current topic index in the round-robin order
   
	public Discv5RRTopicTable() {
        super();
        this.registrationTimes = new TreeMap<Topic, Long>();
        this.roundRobin = false;
        this.endOfRoundTime =  Long.valueOf(-1);
        this.startOfRoundTime =  Long.valueOf(-1);
        this.nextTopicIndex = -1;
        //this.adsPerQueue = this.tableCapacity;
    }
    
    // Returns the current time when xth space is available in the topic table.
    // If slot_number is one, then this returns the time that first space opens up in topic table
    private long getTimeOfNextKAvailableSlot(int slot_number, long curr_time) {
        int remainingCapacity = this.tableCapacity - this.allAds.size();

        if (remainingCapacity >= slot_number) 
            return curr_time;

        if (slot_number > this.tableCapacity) {
            // This can happen if numberOfTopics > tableCapacity, but otherwise shouldn't
            logger.severe("Requested slot is greater than topic table capacity");
            slot_number = this.tableCapacity;
        }

		Iterator<TopicRegistration> it = allAds.iterator();
        int count = 0;
        long waiting_time = 0;
        for(TopicRegistration reg : allAds) {
            waiting_time = this.adLifeTime - (curr_time - reg.getTimestamp());
            count += 1;
            if (count == slot_number)
                break;
        }

        return curr_time + waiting_time;
    }

    protected long getWaitingTime(TopicRegistration reg, long curr_time) {
        Topic topicToRegister = reg.getTopic();
        if (this.roundRobin) {
            // in round robin mode
            Long reg_time = this.registrationTimes.get(topicToRegister);
            if (reg_time != null && reg_time > curr_time) {
                return reg_time - curr_time;
            }
            else {
                return this.endOfRoundTime;
            }
        }
        else { // not in round-robin mode (table is not full)
            return super.getWaitingTime(reg, curr_time);
        }
    }

    private int getNumberOfCompetingTickets() {
        int numOfTickets = 0;
        for (Map.Entry<Topic,ArrayList<Ticket>> entry : this.competingTickets.entrySet()) {
            ArrayList<Ticket> ticketList = entry.getValue();
            numOfTickets += ticketList.size();
        }
        return numOfTickets;

    }

    private int getNumberOfCompetingTopics() {

        int numOfTopics = 0;
        for (Map.Entry<Topic,ArrayList<Ticket>> entry : this.competingTickets.entrySet()) {
            ArrayList<Ticket> ticketList = entry.getValue();
            if (ticketList.size() > 0 )
                numOfTopics += 1; 
        }

        return numOfTopics;
    }
    
    protected Ticket [] makeRegisterDecision(long curr_time) {  
        // update topic table (remove expired ads)
        updateTopicTable(curr_time);
        int remainingCapacity = this.tableCapacity - this.allAds.size();
        int numOfCompetingTopics = getNumberOfCompetingTopics();
        if ( this.roundRobin && (numOfCompetingTopics > remainingCapacity) && (this.nextTopicIndex >= this.registrationTimes.keySet().size() ) ) {
            scheduleRoundRobin(curr_time);
        }
        else if ( !this.roundRobin && (numOfCompetingTopics > remainingCapacity) ) {
            this.roundRobin = true;
            scheduleRoundRobin(curr_time);
        }
        if ( this.roundRobin )
            return makeRegisterDecisionRoundRobin(curr_time);
        else
            return super.makeRegisterDecision(curr_time);
    }

    // Make registration decision in round-robin order 
    // NOTE: adsPerQueue limit is not used when determining registration
    private Ticket [] makeRegisterDecisionRoundRobin(long curr_time) {
        Topic current_topic = null;

        int indx = 0;
        for (Topic topic : this.registrationTimes.keySet()) {
            if ( indx == this.nextTopicIndex ) {
                current_topic = topic;
            }
            indx++;    
        }
        assert current_topic != null;
        
        this.nextTopicIndex += 1;

        ArrayList<Ticket> ticketList = this.competingTickets.get(current_topic);
        Collections.sort(ticketList);

        boolean first = true;
        for(Ticket ticket: ticketList) {
            
            if (first &&  (this.allAds.size() < tableCapacity) ) { //accepted ticket
                TopicRegistration reg = new TopicRegistration(ticket.getSrc(), ticket.getTopic(), curr_time);
                reg.setTimestamp(curr_time);
                first = false;
                KademliaObserver.reportCumulativeTime(ticket.getTopic(), ticket.getCumWaitTime(),Util.logDistance(ticket.getTopic().getTopicID(),hostID));
                ticket.setRegistrationComplete(true);
                ticket.setWaitTime(0);
            }
            else {
                assert !first; 
                ticket.setRegistrationComplete(false);
                ticket.setWaitTime(this.endOfRoundTime);
                long waiting_time = this.endOfRoundTime - curr_time;
                assert waiting_time > 0;
                KademliaObserver.reportWaitingTime(ticket.getTopic(), waiting_time,Util.logDistance(ticket.getTopic().getTopicID(),hostID));
            }
        }
        Ticket [] tickets = (Ticket []) ticketList.toArray(new Ticket[ticketList.size()]);
        return tickets;
    }

    // Computes a registration time for each topic with non-empty competing tickets.
    // The round-robin registration for each topic is done according to the 
    // scheduled registration time.
    private void scheduleRoundRobin(long curr_time) {
        // NOTE: the schedule does not consider adsPerQueue limit

        this.registrationTimes.clear();

        // Identify the topics with competing tickets and add them to Sorted Map
        for (Map.Entry<Topic,ArrayList<Ticket>> entry : this.competingTickets.entrySet()) {
            Topic topic = entry.getKey();
            ArrayList<Ticket> ticketList = entry.getValue();
            if ( ( ticketList != null ) && ( ticketList.size() > 0 ) ) {
                this.registrationTimes.put(topic, null);
            }
        }

        //Identify the waiting times for each topic in round-robin order
        int slot = 1;
        this.startOfRoundTime = getTimeOfNextKAvailableSlot(slot, curr_time);
        for (Map.Entry<Topic, Long> entry : this.registrationTimes.entrySet()) {
            long waiting_time = getTimeOfNextKAvailableSlot(slot, curr_time);
            entry.setValue(waiting_time + KademliaCommonConfig.ONE_UNIT_OF_TIME);
            slot+=1;
        }

        this.endOfRoundTime = getTimeOfNextKAvailableSlot(slot, curr_time);
        this.nextTopicIndex = 0;
    }
}


