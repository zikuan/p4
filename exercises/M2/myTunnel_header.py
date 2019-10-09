
from scapy.all import *
import sys, os

TYPE_MYTUNNEL = 0x1212
TYPE_IPV4 = 0x0800

class MyTunnel(Packet):
    name = "MyTunnel"
    fields_desc = [
        ShortField("pid", 0),
        ShortField("dst_id", 0),
        BitField("query", 0,32),
        BitField("query1", 0,32),
        BitField("query2", 0,32),
        BitField("index", 0,32)
    ]
    def mysummary(self):
        return self.sprintf("pid=%pid%, dst_id=%dst_id%")


bind_layers(Ether, MyTunnel, type=TYPE_MYTUNNEL)
bind_layers(MyTunnel, IP, pid=TYPE_IPV4)

