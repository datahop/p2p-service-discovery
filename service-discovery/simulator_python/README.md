# Topic table simulator 

## Overview

This is a python-based simulator to evaluate the resilience of the waiting time function against attacks that aim to dominate the topic table storage with topic advertisements by malicious nodes. 

See [Waiting Time Computation](https://github.com/datahop/p2p-service-discovery/blob/master/doc/specs.md#waiting-time-function)


## Running the simulator 

$ python table_main.py 

## Configuration parameters:

The main [parameters](https://github.com/datahop/p2p-service-discovery/blob/d22fa15143110266ea57fad4be61e516e1df57d5/service-discovery/simulator_python/table_main.py#L10) are listed below

1) ad_lifetime            (Expiration time of advertisements)
2) capacity               (table capacity)
3) honest_size            (Number of requests by honest nodes)
4) malicious_size         (Number of requests by malicious nodes)
5) occupancy_power        (The occupancy exponent in the waiting time function) 
6) ip_id_power            (The ip and id exponent in the waiting time function)
7) topic_power            (The topic exponent in the waiting time function)
8) attacker_ip_id_num     (The number of IP addresses controlled by the attackers)
9)  base_multiplier       (The value of the base multiplier in the waiting time function)
