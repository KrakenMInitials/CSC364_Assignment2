from collections import namedtuple
import ctypes
import socket
import struct

SocketAddress = tuple[str, int]
User = namedtuple("User", ["username", "user_address", "last_activity"])
uint32 = ctypes.c_uint32

def send_datagram(sender_soc: socket.socket, reciever: SocketAddress, datagram):
    """
    Sends datagram from @sender_doc 
    """
    sender_soc.sendto(datagram, reciever)
    print(f"Sending from {sender_soc} to {reciever}")
    return

def get_message_type(datagram):
    """
    Returns message type from raw datagram
    """
    return struct.unpack("!I", datagram[:4])[0]