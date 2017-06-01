# Axon source routing protocol

## Description

This program implements the Axon protocol for source-routed Ethernet
described in the ANCS '10 paper "Axon: A Flexible Substrate for
Source-routed Ethernet".  The most notable aspect of the Axon protocol
is that, in addition to maintaining a list of forward hops, it also
builds a list of the input ports the packet was received on.  Together,
these hops define a reverse path to the source that uses the same links
as the forward path.

More specifically, the Axon header format is as follows:

|   |   |   |   |   |   |
|---|---|---|---|---|---|
| AxonType : 8 | AxonHdrLength : 16 | FwdHopCount : 8 | RevHopCount : 8 | [FwdHops : 8] | [RevHops : 8] |
|   |   |   |   |   |   |

Note that the number of bits per field both shown above and used in this
program are different from those described in the Axon ANCS '10 paper.
Specifically, the width of the AxonType, FwdHopCount, and RevHopCount
fields have been rounded up to the nearest multiple of 8.

Upon receiving an Axon packet, an Axon switch performs three operations:

1. It validates the header length matches the described number of
   forward hops and reverse hops (and is less than a maximum length).
2. It pushes the input port of the packet onto the list of reverse hops
   and increments the reverse hop count.
3. It pops the head off of the list of forward hops, decrements the
   forward hop count, and then uses this port as an output port for the
   packet.

This program implements a switch that only performs these three operations.

As an example, this program builds upon the P4 concepts introduced by
the EasyRoute protocol, adding in simple TLV processing.  Similar to
EasyRoute, the Axon protocol pops the next hop it should follow off of a
list and decrements a header field.  However, the EasyRoute program can
avoid TLV parsing by only parsing up to the first hop of the source
route and then removing it.   On the other hand, the Axon protocol also
requires that the input port of a packet is pushed onto a list.  This
means that at the list of forward hops must be parsed. Because this list
may be variable in length, this program must perform simple TLV parsing.
However, unlike parsing an IP header, this TLV example is not
complicated by issues related to ordering packet headers.  Additionally,
this program parses the reverse hops of the Axon header, even though
they do not strictly need to be if only Axon forwarding is performed,
i.e., subsequent packet headers do not need to be parsed.

Note that the header stacks parsed in this program (`axon_fwdHop` and
`axon_revHop`) can only hold 64 entries, even though the parser could
try to parse up to 256 entries (8 bits).  This is because of a
limitation in `p4c-bmv2/p4c_bm/gen_json.py`.  If stack sizes of 256 are
used, the script stalls for an extended period of time then generates
the following error: `RuntimeError: maximum recursion depth exceeded`.

Because of this error and because *parser exceptions* are not yet
supported by bmv2, improperly formatted packets can cause simple\_switch
to crash.  In practice, this occurs when IPv6 discovery packets are
received.  In order to avoid this problem, like EasyRoute, this program
also adds a 64bit preamble to the start of packets and requires that
this preamble equals 0.  However, this only mitigates the problem.  A
carefully crafted packet could still exceed the header stack of 64
entries.

### Running the demo

We provide a small demo to let you test the program. It consists of the
following scripts:
- [run_demo.sh](run_demo.sh): compiles the P4 program, starts the switch,
  configures the data plane by running the CLI [commands](commands.txt), and
  starts the mininet console.
- [receive.py](receive.py): listens for Axon formatted packets.  This command is
  intended to be run by a mininet host.
- [send.py](send.py): sends Axon formatted packets from one host to another.
  This command is intended to be run by a mininet host.

To run the demo:
./run_demo.sh will compile your code and create the Mininet network described
above. It will also use commands.txt to configure each one of the switches.
Once the network is up and running, you should type the following in the Mininet
CLI:

- `xterm h1`
- `xterm h3`

This will open a terminal for you on h1 and h3.

On h3 run: `./receive.py`.

On h1 run: `./send.py h1 h3`.

You should then be able to type messages on h1 and receive them on h3. The
`send.py` program finds the shortest path between h1 and h3 using Dijkstra, then
send correctly-formatted packets to h3 through s1 and s3.  Once you are
done testing, quit mininet.  .pcap files will be generated for every
interface (9 files: 3 for each of the 3 switches). You can look at the
appropriate files and check that packets are being processed correctly,
e.g., the forward hops and reverse hops are updated appropriately and
the correct output and input ports are used.
