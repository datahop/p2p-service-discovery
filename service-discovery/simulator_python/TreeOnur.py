class TreeOnurNode:
    def __init__(self):
        self.counter = 0
        self.zero = None
        self.one = None
        self.bound = 0
        self.timestamp = 0  #timestamp for lower-bound state
    
    def getCounter(self):
        return self.counter

    def getBound(self):
        return self.bound

    def getTimestamp(self):
        return self.timestamp

    def increment(self):
        self.counter += 1
        return self.counter
    
    def isLeaf(self):
        if (self.zero is None) and (self.one is None):
            return True
        return False
	    
    def decrement(self):
        self.counter -= 1
        return self.counter

#a structure to calculate diversity between 1 and many IP addresses in O(1)
#score is a similarity metric between the IP being inserted and IPs already in the tree
#1 - the IP is exactly the same (shared all the bits) as all the IPs already in the table
#0 - the IP is completely different (doesn't share a single bit) from IPs already in the table
class TreeOnur:	 
    def __init__(self,  exp=False):
        self.comparators = [128, 64, 32, 16, 8, 4, 2, 1]
        self.root = TreeOnurNode()
        self.exp = exp
        self.currTime = 0 # current simulation time (used for lower bound calculation)
    
    #get the score for an address without actually adding the addr
    def tryAdd(self, addr, time):
        self.currTime = time #update current time
        current = self.root
        score = 0
        effBound = 0
        traversed = ''
        if self.root is not None:
            for depth in range(0, 32):
                parent = current
                if(self.exp == True):
                    score += current.getCounter() * pow(2, depth)
                else:
                    if self.root.getCounter() != 0:
                        score += (current.getCounter()/self.root.getCounter()) * pow(2, depth-24)
            
                octet = int(addr.split('.')[int(depth/8)])
                comparator = self.comparators[int(depth % 8)]
                if((octet & comparator) == 0):
                    current = current.zero
                    traversed += '0'
                else:
                    current = current.one
                    traversed += '1'
            
                if (current is None):
                    current = parent
                    break

            bound = current.getBound()
            print('Bound of current node: ', traversed, ' is ', bound) 
            diff = self.currTime - current.getTimestamp()
            effBound = max(0, bound - diff)
            score = min(1.0, score)
    
        print("TryAdd final score: ", score)

        return (score, effBound)
    
    # find the node corresponding to the  most similar (i.e., longest-prefix match) 
    # ip address in the Trie and update/store the lower-bound state at that node.
    def updateBound(self, addr, bound, currTime):
        current = self.root
        prev = None
        traversed = ''
        self.currTime = currTime
        for depth in range(0, 32):
            prev = current
            octet = int(addr.split('.')[int(depth/8)])
            comparator = self.comparators[int(depth % 8)]
            if((octet & comparator) == 0):
                current = current.zero
                traversed += '0'
            else:
                current = current.one
                traversed += '1'
            
            if (current is None):
                current = prev
                break
        
        diff = self.currTime - current.getTimestamp()
        effBound = current.bound - diff
        if effBound < bound:
        # update lower-bound
            current.bound = bound
            current.timestamp = self.currTime
            print('updating lower bound for ip: ', addr, ' with bound: ', bound, ' and time: ', currTime, ' current eff bound is ', effBound, ' at current node: ', traversed)

    #add an IP to the tree
    def add(self, addr):
        current = self.root
        max_bound = 0
        score = 0
        for depth in range(0, 32):
            parent = current
            if(self.exp == True):
                score += current.getCounter() * pow(2, depth)
            else:
                if self.root.getCounter() != 0:
                    score += (current.getCounter()/self.root.getCounter()) *pow(2, depth-24)
            
            current.increment()
            octet = int(addr.split('.')[int(depth/8)])
            comparator = self.comparators[int(depth % 8)]
            if((octet & comparator) == 0):
                current = current.zero
                if (current is None):
                    current = TreeOnurNode()
                    # propage lower-bound state to new child
                    current.bound = parent.bound
                    current.timestamp = parent.timestamp
                parent.zero = current
            else:
                current = current.one
                if (current is None):
                    current = TreeOnurNode()
                    # propage lower-bound state to new child
                    current.bound = parent.bound
                    current.timestamp = parent.timestamp
                parent.one = current

        #score += current.getCounter()
        current.increment()
        print("Add final score: ")

        return min(score, 1.0)

    # remove the nodes with zero count and propagate their lower bound
    # state upwards and store at first node with count > 0
    def removeAndPropagateUp(self, addr, time):
        current = self.root
        parent = current
        delete = None
        depthToDelete = None
        deleteNode = None
        deleteNodeParent = None
        for depth in range(0, 32):
            current.decrement()
            if (delete is False) and (current.getCounter() == 0): # remove descendants
                delete = True
                depthToDelete = depth
                deleteNode = current
                deleteNodeParent = parent
            octet = int(addr.split('.')[int(depth/8)])
            comparator = self.comparators[int(depth % 8)]
            parent = current
            if((octet & comparator) == 0):
                current = current.zero
            else:
                current = current.one
        current.decrement()

        if delete is True and self.root.getCounter() != 0:
            maxEffBound = 0
            current = deleteNode
            # obtain the highest lower-bound state in the deleted subtree
            for depth in range(depthToDelete, 32):
                effBound = current.getBound() - (time - current.getTimestamp())
                if effBound > maxEffBound:
                    maxEffBound = effBound
                octet = int(addr.split('.')[int(depth/8)])
                comparator = self.comparators[int(depth % 8)]
                if((octet & comparator) == 0):
                    current = current.zero
                else:
                    current = current.one
                
            effBound = current.getBound() - (time - current.getTimestamp())
            if effBound > maxEffBound:
                maxEffBound = effBound

            # delete the subtree rooted at deleteNode
            if deleteNodeParent.one == deleteNode:
                deleteNodeParent.one = None
            elif deleteNodeParent.zero == deleteNode:
                deleteNodeParent.zero = None
            
            # propagate lower-bound state to deleted subtree's parent (if necessary)
            effBound = deleteNodeParent.getBound() - (time - deleteNodeParent.getTimestamp())
            if effBound < maxEffBound:
                deleteNodeParent.bound = maxEffBound
                deleteNodeParent.timestamp = time
