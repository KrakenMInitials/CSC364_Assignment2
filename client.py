import sys, time, threading
from globals import *
from protocols import *
import re

def create_client_socket(server: SocketAddress):
    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"[CLIENT] Client socket created on {server[1]}.")
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e} on port: {server[1]}")
        sys.exit()


def clientListener(client_soc: socket.socket):     #listenerThread
    while (True):
        recieved_datagram = client_soc.recvfrom(1024)

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
                print(x)
        
        elif (msg_type == 2): #who
            users_arr = parse_who_response(recieved_datagram)
            print(f"Users on channel {channel}:")
            for x in users_arr:
                print(x)

        elif ( msg_type == 3): #error
            error_msg = parse_error_response(recieved_datagram)
            raise ValueError(f"Error message from server: \n\t{error_msg}")


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


def cmd_exit():
    datagram = build_logout_request()
    send_datagram(datagram)
    return

    # REQUEST
    #    : Logout the user and exit the client software.


def cmd_join(channel: str):
    return
    # REQUEST
    #    : Join the named channel. If the channel does not exist, create it.
    # CREATES A NEW LISTENER THREAD
    # 1. request server for channel information + UserAddress information
    # 2. SERVER-side does all the work
    # 4. Set channel as ACTIVECHANNEL to be able to send messages

def cmd_leave(channel: str):
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

    # REQUEST
    #   : List the names of all channels. If no channels exist, print an error message.
    # 1. request server for available channels 


def cmd_who(sender_soc, server: SocketAddress, channel: str):
    datagram = build_who_request(channel)
    send_datagram(sender_soc, server, datagram)

    #response handled by listenerThread
    return


def cmd_switch(channel: str):
    return
    # LOCAL
    # : Switch to an existing named channel that user has already joined.
#endregion

def main():
    if (len(sys.argv) != 4):
        print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
        exit(1)

    server_host = sys.argv[1] # hostname or IP address
    server_port = sys.argv[2] # port number
    local_user = sys.argv[3] # username
    print(f"Host: {server_host}")
    print(f"Port: {server_port}")
    print(f"Username: {local_user}")


    server = SocketAddress((server_host, int(server_port)))
    client_soc = create_client_socket(server)
    active_channel = "Common"

    while (True):
        input_prompt = input(">")
        parsed_input = input_prompt.strip().split()

        match parsed_input:
            case ["/exit"]:
                #cmd_exit(server)
                print("executing cmd _exit()")

            case ["/join", channel]:
                #cmd_join(server)
                print(f"executing cmd_join({channel})")

            case ["/leave", channel]:
                #cmd_leave(server)
                print(f"executing cmd_leave({channel})")



            case ["/list"]:
                print("executing cmd_list()")
                cmd_list(server)



            case ["/who", channel]:
                print(f"executing cmd_who({channel})")
                #cmd_who(server)

            case ["/switch", channel]:
                print(f"executing cmd_switch({channel})")
                #cmd_switch(server)

            case ["/"]:
                print(f"Unknown command: {parsed_input}")
            
            case _:
                print(f"executing cmd_say({input_prompt})")

                byte_count = len(input_prompt.encode("utf-8"))
                if (byte_count>64):
                    print("message exceeded 64 bytes: message not sent")
                    continue
                cmd_say(active_channel, input_prompt)


        

    #handle new thread creations and thread management
    #also communicates with the server to get required information directly
    #when to create new thread: 


if __name__ == "__main__":
    main()

