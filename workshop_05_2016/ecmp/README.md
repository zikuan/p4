# Implementing ECMP on top of simple_router.p4

## Introduction

simple_router.p4 is a very simple P4 program which does L3 routing. All the P4
code can be found in the [p4src/simple_router.p4](p4src/simple_router.p4)
file. In this exercise we will try to build ECMP on top of the starter code. We
will be assuming the following network topology:

```
             --------------------------------- nhop-0 10.0.1.1
             |                                        00:04:00:00:00:00
          1 - 00:aa:bb:00:00:00
             |
-------- 3--sw
             |
          2 - 00:aa:bb:00:00:01
             |
             --------------------------------- nhop-1 10.0.2.1
                                                      00:04:00:00:00:01
```

Note that we do not assign IPv4 addresses to the 3 switch interfaces, we do not
need to for this exercise.
We will be sending test packets on interface `3` of the switch. These packets
will have destination IP `10.0.0.1`. We will assume that both `nhop-0` and
`nhop-1` have a path to `10.0.0.1`, which is the final destination of our test
packets.

## Running the starter code

*Before starting make sure that you run `sudo ./veth_setup.sh` to create the
veth pairs required for the demo.*

To compile and run the starter code, simply use `./run_demo.sh`. The
[run_demo.sh](run_demo.sh) script will run the P4 compiler (for bmv2), start the
switch and populate the tables using the CLI commands from
[commands.txt](commands.txt).

When the switch is running, you can send test packets with `sudo
./run_test.py`. Note that this script will take a few seconds to complete. The
test sends a few hundred identical TCP packets through the switch, in bursts,
on port 3. If you take a look at the P4 code and at commands.txt, you will see
that each TCP packet is forwarded out of port 1; since we do not have ECMP
working yet.

## What you need to do

1. In this exercise, you need to update the provided [P4
program](p4src/simple_router.p4) to perform ECMP. When you are done, each
incoming TCP test packet should be forwarded to either port 1 or port 2, based
on the result of a crc16 hash computation performed on the TCP 5-tuple
(`ipv4.srcAddr`, `ipv4.dstAddr`, `ipv4.protocol`, `tcp.srcPort`,
`tcp.dstPort`). You will need to refer to the [P4
spec](http://p4.org/wp-content/uploads/2015/04/p4-latest.pdf) to familiarize
yourself with the P4 constructs you will need.

2. Once you are done with the P4 code, you will need to update
[commands.txt](commands.txt) to configure your new tables.

3. After that you can run the above test again. Once again, you will observe
that all packets go to the same egress port. Don't panic :)! This is because all
packets are identical and therefore are forwarded in the same way, If you add
`--random-dport` when running `sudo ./run_test.py`, you should observe an even
distribution for the ports. This option assigns a random destination port to
each test TCP packet (the 5-tuple is different, so the hash is likely to be
different).

## Hints and directions

1. You can easily check the syntax of your P4 program with `p4-validate <path to
simple_router.p4>`.

2. There are 2 major ways of implementing ECMP on top of simple_router.p4. The
first one requires 2 tables and the use of the
`modify_field_with_hash_based_offset` primitive. The second one uses a single
table with an action profile. You can read about
`modify_field_with_hash_based_offset` and action profiles in the [P4
spec](http://p4.org/wp-content/uploads/2015/04/p4-latest.pdf).

3. If you choose to use the first way (with 2 tables), your first table will
match on the destination IP address and be in charge of computing an index
(using `modify_field_with_hash_based_offset`), while the second table will match
on this computed index to obtain the outgoing interface. This is a high level
view of what needs to be implemented in P4.
```
T1
IP_prefix_1 ---> "random" index in [0, 1] using modify_field_with_hash_based_offset
IP_prefix_2 ---> "random" index in [2, 4] ...
...

T2
index(0)    ---> nhop A
index(1)    ---> nhop B
index(2)    ---> nhop C
index(3)    ---> nhop D
index(4)    ---> nhop E
```
Remember that `T1` and `T2`'s entries will come from your modified commands.txt.
