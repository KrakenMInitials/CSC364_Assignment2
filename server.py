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
        print(f"[{threading.current_thread().name}] Waiting...")
        datagram, client_address = server_soc.recvfrom(1024)
        print(f"[{threading.current_thread().name}] Recieved something...")
        request_queue.put((datagram, client_address))
        #add datagam to request_queue
        #have to consider whether to 
            #tag User during listening or (might be more convenient)
            #tag User in global handler 
    return        

def utility_update_key(oldkey, newkey, theDict: dict):
    old_value = theDict[oldkey]
    theDict.pop(oldkey)
    theDict[newkey] = old_value

def clean_users(server_soc: socket.socket, users_to_channel: dict, channel_to_user: dict):
    users: User
    for users in list(users_to_channel):
        if (time.perf_counter() - users.last_activity):
            handle_logout(server_soc, users.user_address, users_to_channel, channel_to_user)
            datagram = build_error_response("Timed out of server: Please reopen")
            send_datagram(server_soc, users.user_address, datagram)
            print(f"Logging out user {users}")

def global_handler(server_soc: socket.socket, request_queue: queue.Queue, user_to_channel: dict, channel_to_user: dict, server_start_time):
    """
    has to decide which handler to run by peeking into the first 4 bytes of recieved atagrams
    """
    last_clean = time.perf_counter()
    while (True):
        if (time.perf_counter() - last_clean >= 120):
            clean_users(server_soc, user_to_channel, channel_to_user)
            last_clean = time.perf_counter()
        try:
            current_datagram, clientAddress = request_queue.get(timeout=1)
            print(f"Processing {clientAddress} request...")

            msg_type = get_message_type(current_datagram)
            if msg_type == 0:
                handle_login(server_soc, clientAddress, current_datagram, user_to_channel, channel_to_user)
                continue

            user: User
            for user in list(user_to_channel):
                if user.user_address == clientAddress:
                    break

            if not user:
                print("Internal server error: There is no User stored with clientAddress")
                continue
            
            tempUser = User(user.username, user.user_address, time.perf_counter())
            utility_update_key(oldkey=user, newkey=tempUser, theDict=user_to_channel)
            for channels in list(channel_to_user):
                if user in channel_to_user[channels]:
                    channel_to_user[channels].remove(user)
                    channel_to_user[channels].append(tempUser)

            modify_user_data()

            match msg_type:
                case 1:
                    print("LOG: handle_logout()")
                    handle_logout(server_soc, user, current_datagram, user_to_channel, channel_to_user)
                case 2:
                    print("LOG: handle_join()")
                    handle_join(server_soc, user, current_datagram, user_to_channel, channel_to_user)
                case 3:
                    print("LOG: handle_leave()")
                    handle_leave(server_soc, user, current_datagram, user_to_channel, channel_to_user)
                case 4:
                    print("LOG: handle_say()")
                    handle_say(server_soc, user, current_datagram, channel_to_user)
                case 5:
                    print("LOG: handle_list()")
                    handle_list(server_soc, user, current_datagram, channel_to_user)
                case 6:
                    print("LOG: handle_logout()")
                    handle_who(server_soc, user, current_datagram, channel_to_user)
                case 7:
                    print("LOG: handle_keepalive()")
                    handle_keepalive(server_soc, user, current_datagram)
                case _:
                    print(f"Datagram with unknown message type ignored.")
        except queue.Empty:
            continue

#region Handle_ functions
    #handle_ functions have to parse and send datagram as neccessary
    #each handle corresponds to the client protocol NOT the commands

def utility_get_usernames(user_to_channel: dict[User, List[str]]):

    if not user_to_channel:
        return []
    
    result = []
    for x in user_to_channel:
        result.append(x.username)
    return result

def handle_login(server_soc: socket.socket, clientAddress: SocketAddress ,
                 recieved_datagram: bytes, user_to_channel: dict[User, List[str]], channel_to_user: dict[str, List[User]]):
    username = parse_login_request(recieved_datagram)

    existing_usernames = utility_get_usernames(user_to_channel)
    if (username in existing_usernames): #if duplicate username exists
        datagram = build_error_response("Username already exists. Please reopen client.")
        send_datagram(server_soc, clientAddress, datagram)
    else:
        newUser = User(username, clientAddress, time.perf_counter())
        user_to_channel[newUser] = ["Common"]
        if "Common" not in channel_to_user:
            channel_to_user["Common"] = []
        channel_to_user["Common"].append(newUser)
    return
    #verify user doesn't exist yet
    #user to channel
        #add Common to user
    #channel to user
        #add user to Common

    return

def handle_logout(server_soc: socket.socket, user: User, user_to_channel: dict[User, List[str]], channel_to_user: dict[str, List[User]]):
    double_check = False
    for channel in channel_to_user:
        if user in channel_to_user[channel]:
            channel_to_user[channel].remove(user)
            double_check = True
    if (not user_to_channel.pop(user) or (not double_check)):
        print(f"Potential internal server problem")
    return

def handle_join(server_soc: socket.socket, user: User, recieved_datagram: bytes, user_to_channel: dict[User, List[str]], channel_to_user: dict[str, List[User]]):
    channel = parse_join_request(recieved_datagram)

    ####!!!! HANDLE CASE WHERE CLIENT IS ALREADY IN CHANNEL
    
    #add user to channel_to_user
    if channel not in list(channel_to_user): #if channel doesnt exit
        channel_to_user[channel] = [user]
    else: #if channel exists
        if user in channel_to_user[channel]: #if user already in channel
            datagram = build_error_response(f"User is already in channel.")
            send_datagram(server_soc, user.user_address, datagram)
            return    
        channel_to_user[channel].append(user)

    #add channel in user_to_channel
    user_to_channel[user].append(channel)
    return
    # 1. client sends a JOIN request w/ (channel) + UserAddress
    # 2. if channel exists, create channel and create new thread to 
    #    send messages to subscribers
    # 3. if channel does not exist, add UserAddress to channel subscribers

def handle_leave(server_soc: socket.socket, user: User, recieved_datagram: bytes,  user_to_channel: dict[User, List[str]], channel_to_user: dict[str, List[User]]):
    channel = parse_leave_request(recieved_datagram)

    #check if user is in channel, raise error if not
    if user not in channel_to_user[channel]:
        datagram = build_error_response("User is not in the specified channel")
        send_datagram(server_soc, user.user_address, datagram)
        return

    #update channel_to_user
    channel_to_user[channel].remove(user)
    #if channel empty remove it if not Common
    if (channel != "Common") and channel_to_user[channel] == []:
        channel_to_user.pop(channel) 

    #update user_to_channel
    if channel not in user_to_channel[user]:
        print(f"Some internal dictionary management error has occured.")
    user_to_channel[user].remove(channel)
    return
    # 1. client sends a LEAVE request w/ (channel) + UserAddress
    # 2. if channel exists, remove UserAddress from channel subscribers
    # 3. if user is not in the channel, print error message
    # 4. if channel does not exist, print error message
    # 5. if channel is empty, remove channel from server

def handle_say(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_user: dict[str, List[User]]):
    channel, msg = parse_say_request(recieved_datagram)

    if channel == "Common":
        print("Potential internal server error")


    if channel not in channel_to_user:
        response_datagram = build_error_response("Active Channel doesn't exist.")
        send_datagram(server_soc, user.user_address, response_datagram)
    elif user not in list(channel_to_user[channel]):
        response_datagram = build_error_response("User attempted to message a channel they are not a part of.")
        send_datagram(server_soc, user.user_address, response_datagram)
    else:
        response_datagram = build_say_response(channel, user.username, msg)
        for users in channel_to_user[channel]:
            send_datagram(server_soc, users.user_address, response_datagram)

def handle_list(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_user: dict[str, List[User]]):
    #no need parsing parse_list_request() returns None and isnt required
    channel_list = list(channel_to_user)
    if (len(channel_list) == 0):
        response_datagram = build_error_response("There are no channels created on the server.")
    else:
        response_datagram = build_list_response(channel_list)
    send_datagram(server_soc, user.user_address, response_datagram)
    return

def handle_who(server_soc: socket.socket, user: User, recieved_datagram: bytes, channel_to_user: dict[str, List[User]]):
    channel =  parse_who_request(recieved_datagram)

    users_list = list(channel_to_user[channel])
    if (len(users_list) == 0):
        response_datagram = build_error_response(f"There are no users active in the channel {channel}.")
    else:
        usernames_list = [x.username for x in users_list]
        response_datagram = build_who_response(channel, usernames_list)
    send_datagram(server_soc, user.user_address, response_datagram)
    return

def handle_keepalive(server_soc: socket.socket, user: User, recieved_datagram: bytes):
    return

#endregion

def main():
    if (len(sys.argv) != 3):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)
        
    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number

    user_to_channel: dict[User, List[str]] = {}
    channel_to_user: dict[str, List[User]] = {}     
    request_queue = queue.Queue()
    server_soc = create_server_socket((server_host, int(server_port)))

    server_start_time = time.perf_counter()

    threading.Thread(target=serverListener, name="listenerThread", args=(server_soc,request_queue,server_start_time)).start()

    global_handler(server_soc, request_queue, user_to_channel, channel_to_user, server_start_time)

if __name__ == "__main__":
    main()
    # main thread processes all commands from all clients
    #MIGHT NOT NEED ANY THREADING

# def cmd_join(channel: String):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + UserAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

