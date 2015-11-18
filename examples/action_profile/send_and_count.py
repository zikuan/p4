from scapy.all import *
import sys
import threading
import time


big_lock = threading.Lock()
counts = {}


class Receiver(threading.Thread):
    def __init__(self, port, veth):
        threading.Thread.__init__(self)
        self.daemon = True
        self.port = port
        self.veth = veth

    def received(self, p):
        # no need for a lock, each thread is accessing a different key, and the
        # dictionary itself is not modified
        counts[self.port] += 1

    def run(self):
        sniff(iface=self.veth, prn=lambda x: self.received(x))


def main():
    try:
        num_packets = int(sys.argv[1])
    except:
        num_packets = 200
    print "Sending", num_packets, "packets on port 0"

    port_map = {
        1: "veth3",
        2: "veth5",
        3: "veth7",
        4: "veth9"
    }

    for port in port_map:
        counts[port] = 0
    for port, veth in port_map.items():
        Receiver(port, veth).start()

    for i in xrange(num_packets):
        src = "11.0.%d.%d" % (i >> 256, i % 256)
        p = Ether(src="aa:aa:aa:aa:aa:aa") / IP(dst="10.0.0.1", src=src) / TCP() / "aaaaaaaaaaaaaaaaaaa"
        sendp(p, iface="veth1", verbose=0)

    time.sleep(1)

    for port in port_map:
        print "port {0}: {1} packets ({2}%)".format(
            port, counts[port], (100 * counts[port]) / num_packets
        )

if __name__ == '__main__':
    main()
