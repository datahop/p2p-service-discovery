package main.java.peersim.util;

public class CircularQueue {
		 // Array used to implement the queue.
		 private long[] queueRep;
		 private int size, front, rear;
		 
		 // Length of the array used to implement the queue.
		 private  final int CAPACITY; //Default Queue size

		 // Initializes the queue to use an array of default length.
		 public CircularQueue (){
		  CAPACITY = 16;
		  queueRep = new long [CAPACITY];
		  size  = 0; front = 0; rear  = 0;
		 }
		 
		 // Initializes the queue to use an array of given length.
		 public CircularQueue (int cap){
		  CAPACITY = cap;
		  queueRep = new long [cap];
		  size  = 0; front = 0; rear  = 0;
		 }
		 
		 // Inserts an element at the rear of the queue. This method runs in O(1) time.
		 public void enQueue (long data){  

		   size++;
		   if(size>CAPACITY)size=CAPACITY;

		   queueRep[rear] = data;
		   rear = (rear+1) % CAPACITY;
		   //System.out.println("Rear "+rear+" front "+front);
		 }

		 // Removes the front element from the queue. This method runs in O(1) time.
		 public long deQueue () throws IllegalStateException{
		  // Effects:   If queue is empty, throw IllegalStateException,
		  // else remove and return oldest element of this
		  if (size == 0)
		   throw new IllegalStateException ("Queue is empty: Underflow");
		  else {
		   size--;
		   long data = queueRep [ (front % CAPACITY) ];
		   queueRep [front] = Integer.MIN_VALUE;
		   front = (front+1) % CAPACITY;
		   return data;
		  }
		 }

		 // Checks whether the queue is empty. This method runs in O(1) time.
		 public boolean isEmpty(){ 
		  return (size == 0); 
		 }
		 
		 // Checks whether the queue is full. This method runs in O(1) time.
		 public boolean isFull(){ 
		  return (size == CAPACITY); 
		 }
		 
		 // Returns the number of elements in the queue. This method runs in O(1) time.
		 public int size() {
		  return size;
		 }
		 
		 public long average() {
			 
			 long sum=0;
			 for(int i=0;i<queueRep.length;i++) {
				sum+=queueRep[i]; 
			 }
			 return sum/queueRep.length;
		 }
		 
		 public boolean isGrowing() {
			 for(int i=1;i<queueRep.length;i++) {
				if(queueRep[i]<queueRep[i-1])
					return false; 
			 }
			 return true;
		 }
		 
		 // Returns a string representation of the queue as a list of elements, with
		 // the front element at the end: [ ... , prev, rear ]. This method runs in O(n)
		 // time, where n is the size of the queue. 
		 public String toString(){
		  String result = "[";
		  for (int i = CAPACITY; i > 0; i--){
		   int pos=rear-i;
		   if(pos<0)pos=rear-i+CAPACITY;
		   result += Long.toString(queueRep[pos]);
		   if (i > 1) {
		    result += ", ";
		   }
		  }
		  result += "]";
		  return result;
		 }
		 
}
