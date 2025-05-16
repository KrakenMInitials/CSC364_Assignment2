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
        print(f"[SERVER] Server socket created on {socket_address[0]}:{socket_address[1]}.")
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e} on port: {socket_address[1]}")
        sys.exit()


def serverListener(server_soc : socket.socket, request_queue: queue.Queue, server_start_time): #thread to handle all incoming messages and queue in queue
    while (True):
        try:
            #print(f"[{threading.current_thread().name}] Waiting...")
            datagram, client_address = server_soc.recvfrom(1024)
            #print(f"[{threading.current_thread().name}] Recieved something...")
            request_queue.put((datagram, client_address))
        except ConnectionResetError as cre:
            print(f"{client_address} connection was reset: ignoring datagram")
            continue
        #add datagam to request_queue
        #have to consider whether to 
            #tag User during listening or (might be more convenient)
            #tag User in global handler 
    return        

def clean_users(user_store:dict, server_soc: socket.socket, user_to_channels: dict, channel_to_users: dict):
    logout_list = []
    
    user: User

    for user in user_store.values():
        #print(f"{time.perf_counter()}: clean log: {user.username} {user.last_activity}")
        #print(f"Checking user {user.username} — last activity: {user.last_activity}, now: {time.perf_counter()}")
        if (time.perf_counter() - user.last_activity >= 20):
            logout_list.append(user)

    for user in logout_list:
        handle_logout(user_store, server_soc, user, user_to_channels, channel_to_users)
        datagram = build_error_response("Timed out of server: Please reopen")
        send_datagram(server_soc, user.user_address, datagram)
        print(f"{time.perf_counter()}: Logging out user {user.username}")

def global_handler(user_store:dict, server_soc: socket.socket, request_queue: queue.Queue, user_to_channels: dict, channel_to_users: dict, server_start_time):
    """
    has to decide which handler to run by peeking into the first 4 bytes of recieved atagrams
    """
    last_clean = time.perf_counter()
    while (True):
        time.sleep(1)
        if (time.perf_counter() - last_clean >= 20):
            clean_users(user_store, server_soc, user_to_channels, channel_to_users)
            last_clean = time.perf_counter()
        try:
            current_datagram, clientAddress = request_queue.get(timeout=1)
            #print(f"Processing {clientAddress} request...")

            msg_type = get_message_type(current_datagram)
            if msg_type == 0:
                handle_login(user_store, server_soc, clientAddress, current_datagram, user_to_channels, channel_to_users)
                continue

            user: User
            missed = True
            for user in user_store.values():
                if (user.user_address == clientAddress):
                    user_store[user.username] = user_store[user.username]._replace(last_activity=time.perf_counter())
                    missed = False
                    break

            if missed:
                print("There is no User stored with clientAddress")
                datagram = build_error_response("Invalid session: reopen client")
                send_datagram(server_soc, clientAddress, datagram)
                continue
            
            #still need to overwrite user Object because namedtuple is immutable

            match msg_type:
                case 1:
                    handle_logout(user_store, server_soc, user, user_to_channels, channel_to_users)
                case 2:
                    handle_join(server_soc, user, current_datagram, user_to_channels, channel_to_users)
                case 3:
                    handle_leave(server_soc, user, current_datagram, user_to_channels, channel_to_users)
                case 4:
                    handle_say(user_store, server_soc, user, current_datagram, channel_to_users)
                case 5:
                    handle_list(server_soc, user, current_datagram, channel_to_users)
                case 6:
                    handle_who(server_soc, user, current_datagram, channel_to_users)
                case 7:
                    handle_keepalive(user_store, user)
                case _:
                    print(f"Datagram with unknown message type ignored.")
        except queue.Empty:
            continue

#region Handle_ functions
    #handle_ functions have to parse and send datagram as neccessary
    #each handle corresponds to the client protocol NOT the commands

def handle_login(user_store:dict, server_soc: socket.socket, clientAddress: SocketAddress ,
                 recieved_datagram: bytes, user_to_channels: dict[User, List[str]], channel_to_users: dict[str, List[User]]):
    username = parse_login_request(recieved_datagram)

    if (username in list(user_to_channels)): #if duplicate username exists
        datagram = build_error_response("Username already exists. Please reopen client.")
        send_datagram(server_soc, clientAddress, datagram)
    else:
        user_to_channels[username] = ["Common"]
        user_store[username] = User(username, clientAddress, time.perf_counter())
        if "Common" not in channel_to_users:
            channel_to_users["Common"] = []
        channel_to_users["Common"].append(username)
    return
    #verify user doesn't exist yet
    #user to channel
        #add Common to user
    #channel to user
        #add user to Common

    return

def handle_logout(user_store:dict, server_soc: socket.socket, user: User, user_to_channels: dict[User, List[str]], channel_to_users: dict[str, List[User]]):
    double_check = False

    for channel in channel_to_users:
        if user.username in channel_to_users[channel]:
            channel_to_users[channel].remove(user.username)
            double_check = True
    if (not user_to_channels.pop(user.username) or (not user_store.pop(user.username))or (not double_check)):
        print(f"Potential internal dict management problem")
    return

def handle_join(server_soc: socket.socket, user: User, recieved_datagram: bytes, user_to_channels: dict[User, List[str]], channel_to_users: dict[str, List[User]]):
    channel = parse_join_request(recieved_datagram)

    ####!!!! HANDLE CASE WHERE CLIENT IS ALREADY IN CHANNEL
    
    #add user to channel_to_users
    if channel not in list(channel_to_users): #if channel doesnt exit
        channel_to_users[channel] = [user.username]
    else: #if channel exists
        if user.username in channel_to_users[channel]: #if user already in channel
            datagram = build_error_response(f"User is already in channel.")
            send_datagram(server_soc, user.user_address, datagram)
            return    
        channel_to_users[channel].append(user.username)

    #add channel in user_to_channels
    user_to_channels[user.username].append(channel)
    return
    # 1. client sends a JOIN request w/ (channel) + UserAddress
    # 2. if channel exists, create channel and create new thread to 
    #    send messages to subscribers
    # 3. if channel does not exist, add UserAddress to channel subscribers

def handle_leave(server_soc: socket.socket, user: User, recieved_datagram: bytes,  user_to_channels: dict[User, List[str]], channel_to_users: dict[str, List[User]]):
    channel = parse_leave_request(recieved_datagram)

    #check if user is in channel, raise error if not
    if user.username not in channel_to_users[channel]:
        datagram = build_error_response("User is not in the specified channel")
        send_datagram(server_soc, user.user_address, datagram)
        return

    #update channel_to_users
    channel_to_users[channel].remove(user.username)
    #if channel empty remove it if not Common
    if (channel != "Common") and channel_to_users[channel] == []:
        channel_to_users.pop(channel) 

    #update user_to_channels
    if channel not in user_to_channels[user.username]:
        print(f"Some internal dictionary management error has occured.")
    user_to_channels[user.username].remove(channel)
    return
    # 1. client sends a LEAVE request w/ (channel) + UserAddress
    # 2. if channel exists, remove UserAddress from channel subscribers
    # 3. if user is not in the channel, print error message
    # 4. if channel does not exist, print error message
    # 5. if channel is empty, remove channel from server

def handle_say(user_store: dict, server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_users: dict[str, List[User]]):
    channel, msg = parse_say_request(recieved_datagram)

    if channel not in channel_to_users:
        response_datagram = build_error_response("Active Channel doesn't exist.")
        send_datagram(server_soc, user.user_address, response_datagram)
    elif user.username not in list(channel_to_users[channel]):
        response_datagram = build_error_response("User attempted to message channel they are not in. \'/join <ch>\'")
        send_datagram(server_soc, user.user_address, response_datagram)
    else:
        response_datagram = build_say_response(channel, user.username, msg)
        for usernames in channel_to_users[channel]:
            user = user_store[usernames]
            send_datagram(server_soc, user.user_address, response_datagram)

def handle_list(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_users: dict[str, List[User]]):
    #no need parsing parse_list_request() returns None and isnt required
    channel_list = list(channel_to_users)
    if (len(channel_list) == 0):
        response_datagram = build_error_response("There are no channels created on the server.")
    else:
        response_datagram = build_list_response(channel_list)
    send_datagram(server_soc, user.user_address, response_datagram)
    return

def handle_who(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_users: dict[str, List[User]]):
    channel =  parse_who_request(recieved_datagram)

    users_list = list(channel_to_users[channel])
    if (len(users_list) == 0):
        response_datagram = build_error_response(f"There are no users active in the channel {channel}.")
    else:
        usernames_list = [x for x in users_list]
        response_datagram = build_who_response(channel, usernames_list)
    send_datagram(server_soc, user.user_address, response_datagram)
    return

def handle_keepalive(user_store: dict, user: User):
    user_store[user.username] = user_store[user.username]._replace(last_activity=time.perf_counter())
    print(f"{user_store[user.username].username} pinged to be kept alive.")
    return

#endregion

def main():
    if (len(sys.argv) != 3):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)
        
    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number


    user_to_channels: dict[str, set[str]] = {}       # username → set of channel names
    channel_to_users: dict[str, set[str]] = {}       # channel → set of usernames
    user_store: dict[str, User] = {}                 # username -> User object

    request_queue = queue.Queue()
    server_soc = create_server_socket((server_host, int(server_port)))

    server_start_time = time.perf_counter()

    threading.Thread(target=serverListener, name="listenerThread", args=(server_soc,request_queue,server_start_time)).start()

    global_handler(user_store, server_soc, request_queue, user_to_channels, channel_to_users, server_start_time)

if __name__ == "__main__":
    main()
    # main thread processes all commands from all clients
    #MIGHT NOT NEED ANY THREADING

# def cmd_join(channel: String):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + UserAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

