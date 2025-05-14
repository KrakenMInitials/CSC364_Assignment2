import sys, time, struct, threading
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


def clientListener(client_soc: socket.socket):     #will create a socket to listen to and handle connections
    while (True):
        raw_message = client_soc.recvfrom(1024)
        channel, user, text = parse_say_response(raw_message)
        print(f"[{channel}][{user}] {text}")

#region Command functions
    # /exit
    # /join <channel>
    # /leave <channel>
    # /list: List the names of all channels.
    # /who <channel>: List the users who are on the named channel.
    # /switch <channel>: Switch to an existing named channel that user has already joined.


def cmd_exit():
    datagram = build_logout_request(0)
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
    return
    # REQUEST
    #   : List the names of all channels. If no channels exist, print an error message.
    # 1. request server for available channels 

def cmd_who(channel: str):
    return
    # REQUEST
    #  : List the users who are on the named channel. If the channel does not exist, print an error message.
    # 2. request server for users on a channel

def cmd_switch(channel: str):
    return
    # LOCAL
    # : Switch to an existing named channel that user has already joined. If the user is not in the channel, print an error message.
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

    while (True):
        command = input(">")
        parsed_command = command.strip().split()
        match parsed_command:
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

            case _:
                print(f"Unknown command: {parsed_command}")
                
    #handle new thread creations and thread management
    #also communicates with the server to get required information directly
    #when to create new thread: 


if __name__ == "__main__":
    main()

