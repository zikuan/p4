from scapy.all import *

sniff(iface = "veth7", prn = lambda x: hexdump(x))
