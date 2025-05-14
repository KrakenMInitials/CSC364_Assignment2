from collections import namedtuple
import ctypes
import socket

SocketAddress = tuple[str, int]
User = namedtuple("User", ["username", "user_address", "last_activity"])
uint32 = ctypes.c_uint32

def send_datagram(sender_soc: socket.socket, reciever: SocketAddress, datagram):
    sender_soc.sendto(datagram, reciever)
    return