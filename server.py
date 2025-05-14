import sys
import time
import threading
from protocols import *
from typing import List
import queue
from globals import *

def create_server_socket(socket_address: SocketAddress):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.bind(socket_address)
        print(f"[SERVER] Server socket created on {socket_address[1]}.")
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e} on port: {socket_address[1]}")
        sys.exit()


def serverListener(server_soc : socket.socket, request_queue: queue.Queue): #thread to handle all incoming messages and queue in queue
    while (True):
        datagram, client_address = server_soc.recvfrom(1024)
        request_queue.put((datagram, client_address))
        #add datagam to request_queue
        #have to consider whether to 
            #tag User during listening or (might be more convenient)
            #tag User in global handler 
    return        

def global_handler(server_soc: socket.socket, request_queue: queue.Queue, user_to_channel: dict, channel_to_user: dict):
    """
    has to decide which handler to run by peeking into the first 4 bytes of recieved atagrams
    """
    while (request_queue.not_empty):
        current_datagram, clientAddress = request_queue.get(timeout=1)

        user: User
        x: User
        for x in list(user_to_channel):
            if x.user_address == clientAddress:
                user = x
        
        msg_type = get_message_type(current_datagram)

        match msg_type:
            case 0:
                handle_login(server_soc, user, current_datagram)

            case 1:
                handle_logout(server_soc, user, current_datagram)

            case 2:
                handle_join(server_soc, user, current_datagram)

            case 3:
                handle_leave(server_soc, user, current_datagram)

            case 4:
                handle_say(server_soc, user, current_datagram)

            case 5:
                handle_list(server_soc, user, current_datagram, channel_to_user)

            case 6:
                handle_who(server_soc, user, current_datagram, channel_to_user)

            case 7:
                handle_keepalive(server_soc, user, current_datagram)

            case _:
                print(f"Datagram with unknown message type ignored.")
        

#region Handle_ functions
    #handle_ functions have to parse and send datagram as neccessary
    #each handle corresponds to the client protocol NOT the commands



def handle_login(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return

def handle_logout(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return

def handle_join(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return
    # 1. client sends a JOIN request w/ (channel) + UserAddress
    # 2. if channel exists, create channel and create new thread to 
    #    send messages to subscribers
    # 3. if channel does not exist, add UserAddress to channel subscribers

def handle_leave(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return
    # 1. client sends a LEAVE request w/ (channel) + UserAddress
    # 2. if channel exists, remove UserAddress from channel subscribers
    # 3. if user is not in the channel, print error message
    # 4. if channel does not exist, print error message
    # 5. if channel is empty, remove channel from server

def handle_say(server_soc: socket.socket, user: User, recieved_datagram: bytes):
     = parse_say_request(recieved_datagram)


def handle_list(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_user):
    #no need parsing parse_list_request() returns None and isnt required

    channel_list = list(channel_to_user)
    if len(channel_list == 0):
        response_datagram = build_error_response("There are no channels created on the server.")
    else:
        response_datagram = build_list_response(channel_list)
    send_datagram(server_soc, user.user_address, response_datagram)


def handle_who(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_user):
    channel =  parse_who_request(recieved_datagram)

    users_list = list(channel_to_user[user.username])
    if len(users_list == 0):
        response_datagram = build_error_response(f"There are no users active in the channel {channel}.")
    else:
        response_datagram = build_who_response(channel, users_list)
    send_datagram(response_datagram)

def handle_keepalive(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return

#endregion

def main():
    if (sys.argc != 3):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)
        
    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number

    user_to_channel: dict[str, List[str]]
    channel_to_user = dict[str, List[User]]     

    request_queue = queue.Queue

    server_soc = create_server_socket((server_host, server_port))



if __name__ == "__main__":
    main()
    # main thread processes all commands from all clients
    #MIGHT NOT NEED ANY THREADING

# def cmd_join(channel: String):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + UserAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

