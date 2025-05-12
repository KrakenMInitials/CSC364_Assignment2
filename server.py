import sys, socket 
import time
import threading
from collections import namedtuple
import struct

def create_datagram(message_type: int, payload_str: str = None) -> bytes:
    if not (0 <= message_type <= 0xFFFFFFFF): #validate messageType is within uint32 range
        raise ValueError("messageType out of range for uint32")
    
    datagram = None

    def build_say(msg_type: int, channel_name: str, user_name: str, text: str) -> bytes:
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
        user_bytes = user_name.encode('utf-8')[:32].ljust(32, b'\x00')
        text_bytes = text.encode('utf-8')[:64].ljust(64, b'\x00')
        return struct.pack("!I32s32s64s", msg_type, channel_bytes, user_bytes, text_bytes)


    def build_list(msg_type: int, channels_count: int, channels_array: list) -> bytes:
        datagram = struct.pack("!II", msg_type, channels_count) # Pack the message type
        
        for i in range(channels_count):
            channel_bytes = channels_array[i].encode('utf-8')[:32].ljust(32, b'\x00')
            datagram += channel_bytes
        return datagram


    def build_who(msg_type: int, users_count: int , channel_name: str, users_array: list) -> bytes:
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
        datagram = struct.pack("!II32s", msg_type, users_count, channel_bytes)

        for i in range(users_count):
            user_bytes = users_array[i].encode('utf-8')[:32].ljust(32, b'\x00')
            datagram += user_bytes
        return datagram

    def build_error(msg_type: int, error_message: str) -> bytes:
        error_bytes = error_message.encode('utf-8')[:64].ljust(64, b'\x00')
        return struct.pack("!I64s", msg_type, error_bytes)

serverAddress = namedtuple("serverAddress", ["host_name", "port_number"])
userAddress = namedtuple("userAddress", ["host_name", "port_number"])
user = namedtuple("user", ["username", "userAddress"])

class Channel:
    def __init__(self, name: str):
        self.name = name
        self.subscribers = []     

if __name__ == "__main__":
    # main thread processes all commands from all clients

# def cmd_join(channel: String):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + userAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

def handle_join(channel : str, user: userAddress):
    # 1. client sends a JOIN request w/ (channel) + userAddress
    # 2. if channel exists, create channel and create new thread to 
    #    send messages to subscribers
    # 3. if channel does not exist, add userAddress to channel subscribers

def handle_leave(channel : str, user: userAddress):
    # 1. client sends a LEAVE request w/ (channel) + userAddress
    # 2. if channel exists, remove userAddress from channel subscribers
    # 3. if user is not in the channel, print error message
    # 4. if channel does not exist, print error message
    # 5. if channel is empty, remove channel from server

