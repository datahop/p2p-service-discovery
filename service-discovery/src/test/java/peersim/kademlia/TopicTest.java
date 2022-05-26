package peersim.kademlia;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigInteger;
import org.junit.jupiter.api.Test;

public class TopicTest {
  Topic t1, t2;

  @Test
  public void testComparison() {
    BigInteger hostID = new BigInteger("100000000000000000000000000000000000000000000000");
    t1 = new Topic(hostID, "topic1");
    // System.out.println("t1:" + t1);
    t2 = new Topic(hostID, "topic2");
    assertEquals(t1.compareTo(t2), -1);
    // assertEquals(t1.compareTo(t2), 0);
  }
}
