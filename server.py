import sys, socket 
import time
import threading
import struct
from protocols import *
from typing import List
import queue
from globals import *


class Channel:
    def __init__(self, name: str):
        self.name = name
        self.user_to_channel = dict()
        self.channel_to_user = dict()     

def create_server_socket(socket_address: SocketAddress):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.bind(socket_address)
        print(f"[SERVER] Server socket created on {socket_address[1]}.")
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e} on port: {socket_address[1]}")
        sys.exit()


def serverListener(): #thread to handle all incoming messages and queue in queue
    while (True):
        try:
            

def global_handler():
    while (True):
        #if 


def handle_logout(raw_datagram):
    0 = parse_logout(raw_datagram)


def handle_join(channel : str, user: userAddress):
    return
    # 1. client sends a JOIN request w/ (channel) + userAddress
    # 2. if channel exists, create channel and create new thread to 
    #    send messages to subscribers
    # 3. if channel does not exist, add userAddress to channel subscribers


def handle_leave(channel : str, user: userAddress):
    return
    # 1. client sends a LEAVE request w/ (channel) + userAddress
    # 2. if channel exists, remove userAddress from channel subscribers
    # 3. if user is not in the channel, print error message
    # 4. if channel does not exist, print error message
    # 5. if channel is empty, remove channel from server


def main():
    if (sys.argc != 3):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)
        
    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number

    request_queue = queue.Queue

    server_soc = create_server_socket((server_host, server_port))



if __name__ == "__main__":
    main()
    # main thread processes all commands from all clients
    #MIGHT NOT NEED ANY THREADING

# def cmd_join(channel: String):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + userAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

