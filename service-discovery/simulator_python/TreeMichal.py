from re import L
import sys

class TreeMichalNode:
    def __init__(self):
        self.counter = 0
        self.zero = None
        self.one = None
        self.bound = 0
        self.timestamp = 0  #timestamp for lower-bound state
        
    
    def getCounter(self):
        return self.counter

    def getBound(self):
        return 0
        #return self.bound

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
class TreeMichal:	 
    def __init__(self):
        self.comparators = [128, 64, 32, 16, 8, 4, 2, 1]
        self.root = TreeMichalNode()
        self.max_score = 0
        self.currTime = 0 # current simulation time (used for lower bound calculation)
        self.max_depth = 32 # number of bits in an IP address
    
   
    # find the node corresponding to the  most similar (i.e., longest-prefix match) 
    # ip address in the Trie and update/store the lower-bound state at that node.
    def updateBound(self, addr, bound, currTime):
        return
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
    def add(self, addr, time = 0, modifyTree = True):
        #print("!!!!!!!!!! adding", addr)
        if(not modifyTree):
            self.currTime = time
        current = self.root
        effBound = 0
        max_score = 32
        score = 0
        rootCounter = self.root.getCounter()

        if(modifyTree == True):
            self.score_dump = {}
            self.traverse(self.root, 0)

        for depth in range(0, self.max_depth):
            parent = current
            expected = rootCounter/(2**depth)
            #print("depth:", depth, "counter:", current.getCounter(), "expected:", expected, "root counter:", rootCounter, "2^depth:", 2**depth)
            if(current.getCounter() > expected):
                score += 1
                print("adding penalty point at depth", depth)
            
            if(modifyTree):
                current.increment()

            octet = int(addr.split('.')[int(depth/8)])
            comparator = self.comparators[int(depth % 8)]
            if((octet & comparator) == 0):
                current = current.zero
                if (current is None):
                    current = TreeMichalNode()
                    # propage lower-bound state to new child
                    current.bound = parent.bound
                    current.timestamp = parent.timestamp
                parent.zero = current
            else:
                current = current.one
                if (current is None):
                    current = TreeMichalNode()
                    # propage lower-bound state to new child
                    current.bound = parent.bound
                    current.timestamp = parent.timestamp
                parent.one = current

        bound = current.getBound()
        diff = self.currTime - current.getTimestamp()
        effBound = max(0, bound - diff)

        #score += current.getCounter()
        expected = rootCounter/(2**self.max_depth)
        #print("depth:", self.max_depth,  "counter:", current.getCounter(), "expected:", expected, "rootCounter:", rootCounter, "2^depth:", 2**self.max_depth)
        if(current.getCounter() > expected):
                score += 1
                #print("adding penalty point")
        
        if(modifyTree):
            current.increment()

        #assert(score >= min_score)
        #assert(score <= max_score)
        #print("Add final score: ", score, " min score: ", min_score, "Max score:", max_score)#, "New max score:", self.max_score)

        if(max_score == 0):
            return 0
        #print("score:", score, "max_score:", max_score)
        assert (0 <= score/max_score <= 1), "score must be between 0 and 1"
        if(modifyTree == True):
            return (score/max_score, effBound, self.score_dump) 
        return (score/max_score, effBound)
        

    
    def traverse (self, node, depth):
        rootCounter = self.root.getCounter()
        expected = rootCounter/(2**depth)

        if (node.zero is not None):
            self.traverse(node.zero, depth + 1)
    
        #print("Visited node ad depth", depth, "and counter:", node.counter)
        if(depth not in self.score_dump):
            self.score_dump[depth] = []
        self.score_dump[depth].append(abs(node.getCounter() - expected))

        if (node.one is not None):
            self.traverse (node.one, depth + 1)


    # remove the nodes with zero count and propagate their lower bound
    # state upwards and store at first node with count > 0
    def removeAndPropagateUp(self, addr, time):
        current = self.root
        parent = current
        delete = None
        depthToDelete = None
        deleteNode = None
        deleteNodeParent = None
        for depth in range(0, self.max_depth):
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
            for depth in range(depthToDelete, self.max_depth):
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
