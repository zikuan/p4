from scapy.all import *
import sys
import threading


class Receiver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def received(self, p):
        print "Received packet on port 3, exiting"
        sys.exit(0)

    def run(self):
        sniff(iface="veth7", prn=lambda x: self.received(x))


def main():
    Receiver().start()

    p = Ether(src="aa:aa:aa:aa:aa:aa") / IP(dst="10.0.1.10") / TCP() / "aaaaaaaaaaaaaaaaaaa"

    print "Sending packet on port 0, listening on port 3"
    time.sleep(1)
    sendp(p, iface="veth1", verbose=0)


if __name__ == '__main__':
    main()
