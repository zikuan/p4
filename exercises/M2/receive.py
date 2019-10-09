#!/usr/bin/env python
import sys
import struct
import os

from scapy.all import sniff, sendp, hexdump, get_if_list, get_if_hwaddr
from scapy.all import Packet, IPOption
from scapy.all import ShortField, IntField, LongField, BitField, FieldListField, FieldLenField
from scapy.all import IP, TCP, UDP, Raw
from scapy.layers.inet import _IPOption_HDR
from myTunnel_header import MyTunnel

indexes = []
def isIdealPermutation(A):
    x_ = 0
    for x in range(len(A)):
        for j in xrange(x+1, len(A)):
            if A[x] > A[j] :
                x_ += 1
    return x_

def get_if():
    ifs=get_if_list()
    iface=None
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def handle_pkt(pkt):
    if MyTunnel in pkt or (TCP in pkt and pkt[TCP].dport == 1234):
        print "got a packet"
        pkt.show2()
        indexes.append(pkt[MyTunnel].index)
#        hexdump(pkt)
#        print "len(pkt) = ", len(pkt)
        sys.stdout.flush()


def main():
    ifaces = filter(lambda i: 'eth' in i, os.listdir('/sys/class/net/'))
    iface = ifaces[0]
    print "sniffing on %s" % iface
    sys.stdout.flush()
    sniff(iface = iface,
          prn = lambda x: handle_pkt(x))
    print indexes
    print isIdealPermutation(indexes)

if __name__ == '__main__':
    main()