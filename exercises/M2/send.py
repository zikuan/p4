#!/usr/bin/env python
import argparse
import sys
import socket
import random
import struct
import string


from scapy.all import sendp, send, get_if_list, get_if_hwaddr
from scapy.all import Packet
from scapy.all import Ether, IP, UDP, TCP
from myTunnel_header import MyTunnel

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """
    randomLength = random.randint(stringLength,stringLength*2)
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(randomLength))

def get_if():
    ifs=get_if_list()
    iface=None # "h1-eth0"
    for i in get_if_list():
        if "eth0" in i:
            iface=i
            break;
    if not iface:
        print "Cannot find eth0 interface"
        exit(1)
    return iface

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ip_addr', type=str, help="The destination IP address to use")
    #parser.add_argument('message', type=str, help="The message to include in packet")
    parser.add_argument('--dst_id', type=int, default=None, help='The myTunnel dst_id to use, if unspecified then myTunnel header will not be included in packet')
    args = parser.parse_args()

    addr = socket.gethostbyname(args.ip_addr)
    dst_id = args.dst_id
    iface = get_if()

    for i in range(100):
        
        print "sending on interface {} to dst_id {}".format(iface, str(dst_id))
        pkt =  Ether(src=get_if_hwaddr(iface), dst='ff:ff:ff:ff:ff:ff')
        pkt = pkt / MyTunnel() / IP(dst=addr) / TCP(dport=1234, sport=random.randint(49152,65535)) /randomString(50) 
        pkt.show2()
#    hexdump(pkt)
#    print "len(pkt) = ", len(pkt)
        sendp(pkt, iface=iface, verbose=False)

if __name__ == '__main__':
    main()
