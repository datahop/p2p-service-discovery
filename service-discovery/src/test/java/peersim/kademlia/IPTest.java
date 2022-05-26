package peersim.kademlia;

import org.junit.jupiter.api.Test;

public class IPTest {
  int[] comparators = new int[] {128, 64, 32, 16, 8, 4, 2, 1};
  TreeNode root;

  public void printBits(String addr) {
    String[] octets = addr.split("\\.");
    System.out.println("Addr:" + addr);
    // System.out.println("octet size:" + octets.length);
    for (String octet : octets) {
      // System.out.print("Octet: " + octet);
      int octetInt = Integer.parseInt(octet);
      // System.out.print(Integer.toBinaryString(octetInt) + ".");
    }
    // System.out.println();
    for (String octet : octets) {
      int octetInt = Integer.parseInt(octet);
      for (int comparator : comparators) {
        // System.out.println("octetInt: " + octetInt + " comparator: " + comparator);
        if ((octetInt & comparator) == 0) {
          ; // System.out.print("0");
        } else {
          ; // System.out.print("1");
        }
      }
      // System.out.print(".");
    }
    // System.out.println();
  }

  @Test
  public void testIPs() {
    printBits("127.0.0.1");
    this.add("127.0.0.1");
    this.add("127.0.0.1");
    System.out.println("~~~~~~~~~~~~~~~~~~~~~~");
    /*printBits("255.255.255.255");
    this.add("255.255.255.255");
    System.out.println("~~~~~~~~~~~~~~~~~~~~~~");
    printBits("192.168.0.2");
    this.add("192.168.0.2");
    System.out.println("~~~~~~~~~~~~~~~~~~~~~~");*/
  }

  @Test
  public void compareAddresses() {
    String addr1 = new String("192.168.1.2");
    String addr2 = new String("192.168.1.3");

    String addr3 = new String("200.34.32.21");
    String addr4 = new String("80.34.23.23");

    if (Util.compareAddr(addr1, addr2))
      System.out.println("Addr1:" + addr1 + " and Addr2:" + addr2 + " are same /24");
    if (!Util.compareAddr(addr3, addr4))
      System.out.println("Addr3:" + addr3 + " and Addr4:" + addr4 + " are not");

    assert (Util.compareAddr(addr1, addr2));
    assert (!Util.compareAddr(addr3, addr4));
  }

  class TreeNode {
    private int counter;
    private TreeNode zero;
    private TreeNode one;

    TreeNode() {
      this.counter = 0;
      zero = null;
      one = null;
    }

    public int getCounter() {
      return this.counter;
    }

    public int increment() {
      return ++this.counter;
    }

    public int decrement() {
      return --this.counter;
    }
  }

  public int add(String addr) {
    Object[] result = addRecursive(root, addr, 0);
    root = (TreeNode) result[0];
    int score = (int) result[1];
    // System.out.println("Final score: " + score + " Max score: " + " My score: " +
    // (root.getCounter()-1) * 528);
    return score;
  }

  private Object[] addRecursive(TreeNode current, String addr, int depth) {
    if (current == null) {
      current = new TreeNode();
    }
    int score = current.getCounter() * depth;
    // System.out.println("Increment counter to " + current.increment());

    if (depth < 32) {
      // System.out.println("Octet: " + addr.split("\\.")[depth/8]);
      int octet = Integer.parseInt(addr.split("\\.")[depth / 8]);
      int comparator = comparators[depth % 8];
      Object[] result = null;
      if ((octet & comparator) == 0) {
        // System.out.println("Going towards 0");
        result = addRecursive(current.zero, addr, depth + 1);
        current.zero = (TreeNode) result[0];
      } else {
        // System.out.println("Going towards 1");
        result = addRecursive(current.one, addr, depth + 1);
        current.one = (TreeNode) result[0];
      }
      score += (int) result[1];
    } else {
      ; // System.out.println("Reached depth " + depth + " going back.");
    }

    return new Object[] {current, score};
  }
}
