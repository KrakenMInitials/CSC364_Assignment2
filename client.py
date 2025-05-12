import sys, socket, time, struct, threading
from collections import namedtuple
from server import serverAddress, userAddress, user
import ctypes
uint32 = ctypes.c_uint32

if (sys.argc != 3){
    print(f"Invalid arguments: <hostname> <portnumber> <username> (expected 3)")
    exit(1)
}

host = sys.argv[1] # hostname or IP address
port = sys.argv[2] # port number
user = sys.argv[3] # username


def create_socket(host, port):

    try:
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print(f"[CLIENT] Client socket created on {port}.")
        return soc
    except socket.error as e:
        print(f"Socket creation failed with error: {e} on port: {port}")
        sys.exit()






























def create_datagram(message_type: int, payload_str: str = None) -> bytes:
    if not (0 <= message_type <= 0xFFFFFFFF): #validate messageType is within uint32 range
        raise ValueError("messageType out of range for uint32")
    
    datagram = None
    
    def build_login(msg_type: int, channel_name: str) -> bytes:
        # Ensure payload is 32-byte padded UTF-8
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
        # Pack 4-byte type + 32-byte payload
        return struct.pack("!I32s", msg_type, channel_bytes)
    

    def build_logout(msg_type: int) -> bytes:
        return struct.pack("!I", msg_type)


    def build_join(msg_type: int, channel_name: str) -> bytes: 
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
        return struct.pack("!I32s", msg_type, channel_bytes)


    def build_leave(msg_type: int, channel_name: str) -> bytes:
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
        return struct.pack("!I32s", msg_type, channel_bytes)
    

    def build_say(msg_type: int, channel_name: str, text: str) -> bytes:
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
        text_bytes = text.encode('utf-8')[:64].ljust(64, b'\x00')
        return struct.pack("!I32s64s", msg_type, channel_bytes, text_bytes)
   

    def build_list(msg_type: int) -> bytes:
        return struct.pack("!I", msg_type)


    def build_who(msg_type: int, channel_name: str, text: str) -> bytes:
        channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
        return struct.pack("!I32s", msg_type, channel_bytes)


    def build_keepalive(msg_type: int) -> bytes:
        return struct.pack("!I", msg_type)







    if payload_str is None: #Header with type only
        datagram = struct.pack("!I", message_type) # 4 bytes for message type
    else: #Header + payload
        datagram = struct.pack("!I32s", message_type, payload_bytes) # 32 bytes for payload
    return datagram







































def parse_datagram(datagram):
    messageType, payload = struct.unpack("!I32s", datagram)
    payload_str = payload.decode('utf-8').rstrip('\x00')  # remove null bytes
    return messageType, payload_str

def client_listening_thread(): #listends to incoming messages from server 
    data, addr = sock.recvfrom(1024)  # 1024 is safe for all message types


################################################
    # /exit
    # /join <channel>
    # /leave <channel>
    # /list: List the names of all channels.
    # /who <channel>: List the users who are on the named channel.
    # /switch <channel>: Switch to an existing named channel that user has already joined.


#def cmd_exit(): LOCAL
#    : Logout the user and exit the client software.

# def cmd_join(channel: String, user: userAddress):
#    : Join the named channel. If the channel does not exist, create it.
# 1. request server for channel information + userAddress information
# 2. SERVER-side does all the work
# 4. Set channel as ACTIVECHANNEL to be able to send messages

# def cmd_leave(channel: String, user: userAddress):
#   : Leave the named channel. If the user is not in the channel, print an error message.
# 1. request server to leave channel
# 2. SERVER-side does all the work
# 3. Server responds sucess or failure
# 4. if fail, print error message (two different types- no channel, not in channel)

# def cmd_list():
#   : List the names of all channels. If no channels exist, print an error message.
# 1. request server for available channels 

# def cmd_who(channel: String):
#  : List the users who are on the named channel. If the channel does not exist, print an error message.
# 2. request server for users on a channel

# def cmd_switch(channel: String):
# : Switch to an existing named channel that user has already joined. If the user is not in the channel, print an error message.

