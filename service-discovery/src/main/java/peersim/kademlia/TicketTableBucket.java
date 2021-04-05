package peersim.kademlia;

import java.util.ArrayList;
import java.util.List;

import main.java.peersim.util.CircularQueue;
import peersim.core.CommonState;


public class TicketTableBucket extends KBucket {
	
    private List<Integer> seenOccupancy;
    private CircularQueue seenWaitingTimes;
    private int seenNotFull = 0; 
	
	public TicketTableBucket(RoutingTable rTable,int k, int maxReplacements)  {
		super(rTable,k,maxReplacements);
		seenOccupancy = new ArrayList<Integer>();
		seenWaitingTimes = new CircularQueue(KademliaCommonConfig.WAITING_WINDOW_SIZE);

	}
	
	public void reportOccupancy(int occupancy) {
		seenOccupancy.add(occupancy);
	}
	
	public void reportWaitingTime(long waitingTime) {
		seenWaitingTimes.enQueue(waitingTime);
	}
	
	public boolean shallContinueRegistrationOccupancy() {
		int windowSize = Math.min(seenOccupancy.size(), KademliaCommonConfig.STOP_REGISTER_WINDOW_SIZE);
		//System.out.println("STOP_REGISTER_WINDOW_SISZE: " + KademliaCommonConfig.STOP_REGISTER_WINDOW_SIZE + " STOP_REGISTER_MIN_REGS: " + KademliaCommonConfig.STOP_REGISTER_MIN_REGS + " windowsSize:" + windowSize);
		if(seenOccupancy.size() < KademliaCommonConfig.STOP_REGISTER_MIN_REGS || windowSize == 0) {
			//System.out.println("Windows size 0 or seenOccupancy.size() < KademliaCommonConfig.STOP_REGISTER_MIN_REGS");
			return true;
		}
		
		int sumOccupancy = 0;
		int sumSpace = windowSize * KademliaCommonConfig.ADS_PER_QUEUE;
		for(int i = (seenOccupancy.size() - windowSize); i < seenOccupancy.size(); i++) {
		    sumOccupancy += seenOccupancy.get(i);
		}
		
		
		int toss = CommonState.r.nextInt(sumSpace);
		//System.out.println("Flipping coin. sumSpace: " + sumSpace + " seenOccupancy: " + seenOccupancy + " toss: " + toss);
		if(toss < sumOccupancy) {
			return false;
		}
		return true;
	}
	
	public boolean shallContinueRegistrationWaitingTime() {
		int windowSize = Math.min(seenWaitingTimes.size(), KademliaCommonConfig.WAITING_WINDOW_SIZE);
		//System.out.println(seenWaitingTimes.size()+" "+seenWaitingTimes);

		//System.out.println("STOP_REGISTER_WINDOW_SISZE: " + KademliaCommonConfig.STOP_REGISTER_WINDOW_SIZE + " STOP_REGISTER_MIN_REGS: " + KademliaCommonConfig.STOP_REGISTER_MIN_REGS + " windowsSize:" + windowSize);
		if(seenWaitingTimes.size() < KademliaCommonConfig.STOP_REGISTER_MIN_REGS || windowSize == 0) {
			//System.out.println("Windows size 0 or seenOccupancy.size() < KademliaCommonConfig.STOP_REGISTER_MIN_REGS");
			return true;
		}
		
		
		/*int toss = CommonState.r.nextInt(sumSpace);
		//System.out.println("Flipping coin. sumSpace: " + sumSpace + " seenOccupancy: " + seenOccupancy + " toss: " + toss);
		if(toss < sumOccupancy) {
			return false;
		}*/
		return true;
	}


}
