import sys, time, threading
from globals import *
from protocols import *
import re

def create_client_socket():
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e}")
        sys.exit()


def client_listener(client_soc: socket.socket, exit_event: threading.Event, activeChannel: list[str]):     #listenerThread
    client_soc.settimeout(5)
    while (True):
        try:
            recieved_datagram,_ = client_soc.recvfrom(1024)

            #Response can be
            #say response
            #list response
            #who response
            #error_response
            msg_type = get_message_type(recieved_datagram)
            if ( msg_type == 0): #say 
                channel, user, text = parse_say_response(recieved_datagram)
                print(f"[{channel}][{user}] {text}")

            elif (msg_type == 1): #list 
                channels_arr = parse_list_response(recieved_datagram)
                print("Existing channels: ")
                for x in channels_arr:
                    if x == activeChannel[0]:
                        print("   " + str(x) + "*")
                    else:
                        print("   " + str(x))
            
            elif (msg_type == 2): #who
                users_arr, channel = parse_who_response(recieved_datagram)
                print(f"Users on channel {channel}:")
                for x in users_arr:
                    print("   " + str(x))

            elif ( msg_type == 3): #error
                error_msg = parse_error_response(recieved_datagram)
                print(f"[CONSOLE] Error message from server: \n   {error_msg}")
        except socket.timeout:
            #no problems, just quick check for exit_event
            if exit_event.is_set():
                print("listening thread closed.")
                return
            continue
        except Exception as e:
            print(f"[CONSOLE] Exception in client listener thread: {e} \nBut continuing regular operations...")


#region Command functions
    # say <message>
    # /exit
    # /join <channel>
    # /leave <channel>
    # /list: List the names of all channels.
    # /who <channel>: List the users who are on the named channel.
    # /switch <channel>: Switch to an existing named channel that user has already joined.

def cmd_say(sender_soc, server: SocketAddress, active_channel: str, msg: str):
    datagram = build_say_request(active_channel, msg)
    send_datagram(sender_soc, server, datagram)
    return

def login_user(sender_soc, server: SocketAddress, username: str):
    datagram = build_login_request(username)
    send_datagram(sender_soc, server, datagram)
    return

def cmd_exit(server_soc, server: SocketAddress, exit_event: threading.Event):
    datagram = build_logout_request()
    send_datagram(server_soc, server, datagram)
    exit_event.set()
    sys.exit(0)

    # REQUEST
    #    : Logout the user and exit the client software.


def cmd_join(server_soc, server: SocketAddress, channel: str):
    datagram = build_join_request(channel)
    send_datagram(server_soc, server, datagram) 
    return
    # REQUEST
    #    : Join the named channel. If the channel does not exist, create it.
    # CREATES A NEW LISTENER THREAD
    # 1. request server for channel information + UserAddress information
    # 2. SERVER-side does all the work
    # 4. Set channel as ACTIVECHANNEL to be able to send messages

def cmd_leave(server_soc, server: SocketAddress, channel: str):
    datagram = build_leave_request(channel)
    send_datagram(server_soc, server, datagram)
    return
    # REQUEST
    #   : Leave the named channel. If the user is not in the channel, print an error message.
    # 1. request server to leave channel
    # 2. SERVER-side does all the work
    # 3. Server responds sucess or failure
    # 4. if fail, print error message (two different types- no channel, not in channel)


def cmd_list(sender_soc, server: SocketAddress):
    datagram = build_list_request()
    send_datagram(sender_soc, server, datagram)
    #reponse handled by listenerThread
    return


def cmd_who(sender_soc, server: SocketAddress, channel: str):
    datagram = build_who_request(channel)
    send_datagram(sender_soc, server, datagram)
    #response handled by listenerThread
    return


def cmd_switch(activeChannel: str):
    # LOCAL (confirmed, no need server communication)
    #placeholder for completeness 
    return
#endregion

def keepalive(sender_soc, server: SocketAddress, exit_event: threading.Event):
    last_keepalive = time.perf_counter()
    while (True):
        if exit_event.is_set():
            return
        if (time.perf_counter() - last_keepalive >= 10):
            send_datagram(sender_soc, server, build_keepalive_request())
            last_keepalive = time.perf_counter()

def main():
    if (len(sys.argv) != 4):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)

    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number
    local_username = sys.argv[3] # username
    print(f"Host: {server_host}")
    print(f"Port: {server_port}")
    print(f"Username: {local_username}")


    server = SocketAddress((server_host, int(server_port)))
    client_soc = create_client_socket()
    client_soc.bind(("0.0.0.0", 0))
    ip, port = client_soc.getsockname()

    print(f"[CONSOLE] Client socket binded to {ip}:{port}")
    active_channel = ["Common"]

    exit_event = threading.Event()
    threading.Thread(target=client_listener, name="listenerThread", args=(client_soc,exit_event, active_channel,)).start()
    threading.Thread(target=keepalive, name="keepaliveThread",args=(client_soc,server,exit_event)).start()

    print(f"Client logged in.")
    login_user(client_soc, server, local_username)

    last_keepalive = time.perf_counter()

    while (True):

        time.sleep(0.5) #helps seperate outputing '>'
        #might be able to remove after using string Buffer modifications

        input_prompt = input(">")
        parsed_input = input_prompt.strip().split()

        match parsed_input:
            case ["/exit"]:
                print("Exiting...")
                cmd_exit(client_soc, server, exit_event)

            case ["/join", channel]:
                print(f"executing cmd_join({channel})")
                print(f"[CONSOLE] switching local activeChannel to {channel}")
                active_channel[0] = channel
                cmd_join(client_soc, server, channel)

            case ["/leave", channel]:
                print(f"executing cmd_leave({channel})")
                if active_channel[0] == channel:
                    print(f"[CONSOLE] defaulting local activeChannel to Common")
                    active_channel[0] = "Common"
                cmd_leave(client_soc, server, channel)
                

            case ["/list"]:
                cmd_list(client_soc, server)

            case ["/who", channel]:
                cmd_who(client_soc, server, channel)

            case ["/switch", channel]:
                print(f"[CONSOLE] switching local activeChannel to {channel}")
                active_channel[0] = channel

            case s if s[0][0] == '/':
                print(f"[CONSOLE] Unknown command: {parsed_input}")
            
            case _:
                print(f"executing cmd_say({input_prompt})")
                byte_count = len(input_prompt.encode("utf-8"))
                if (byte_count>64):
                    print("[CONSOLE] message exceeded 64 bytes: message not sent")
                    continue
                cmd_say(client_soc, server, active_channel[0], input_prompt)


        

    #handle new thread creations and thread management
    #also communicates with the server to get required information directly
    #when to create new thread: 


if __name__ == "__main__":
    main()

