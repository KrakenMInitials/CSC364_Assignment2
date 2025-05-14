import struct

#region client-side build Functions
def build_login_request(channel_name: str) -> bytes:
    # Ensure payload is 32-byte padded UTF-8
    msg_type = 0
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
    # Pack 4-byte type + 32-byte payload
    return struct.pack("!I32s", msg_type, channel_bytes)

def build_logout_request() -> bytes:
    msg_type = 1
    return struct.pack("!I", msg_type)

def build_join_request(channel_name: str) -> bytes: 
    msg_type = 2
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
    return struct.pack("!I32s", msg_type, channel_bytes)

def build_leave_request(channel_name: str) -> bytes:
    msg_type = 3
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
    return struct.pack("!I32s", msg_type, channel_bytes)

def build_say_request(channel_name: str, text: str) -> bytes:
    msg_type = 4
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00') #pad with null bytes
    text_bytes = text.encode('utf-8')[:64].ljust(64, b'\x00')
    return struct.pack("!I32s64s", msg_type, channel_bytes, text_bytes)

def build_list_request() -> bytes:
    msg_type = 5
    return struct.pack("!I", msg_type)

def build_who_request(channel_name: str) -> bytes:
    msg_type = 6
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
    return struct.pack("!I32s", msg_type, channel_bytes)

def build_keepalive_request() -> bytes:
    msg_type = 7
    return struct.pack("!I", msg_type)
#endregion

#region client-side parse Functions
def parse_say_response(datagram: bytes) -> tuple[str, str, str]:
    _, channel_bytes, user_bytes, text_bytes = struct.unpack("!I32s32s64s", datagram)
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')
    user = user_bytes.rstrip(b'\x00').decode('utf-8')
    text = text_bytes.rstrip(b'\x00').decode('utf-8')
    return channel, user, text

def parse_list_response(datagram: bytes) -> list[str]:
    _, count = struct.unpack("!II", datagram[:8])
    channels = []
    offset = 8
    for _ in range(count):
        (ch_bytes,) = struct.unpack("!32s", datagram[offset:offset+32])
        channels.append(ch_bytes.rstrip(b'\x00').decode('utf-8'))
        offset += 32
    return channels

def parse_who_response(datagram: bytes) -> tuple[str, list[str]]:
    _, count = struct.unpack("!II", datagram[:8])
    channel_bytes = struct.unpack("!32s", datagram[8:40])[0]
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')

    users = []
    offset = 40
    for _ in range(count):
        (user_bytes,) = struct.unpack("!32s", datagram[offset:offset+32])
        users.append(user_bytes.rstrip(b'\x00').decode('utf-8'))
        offset += 32
    return channel, users

def parse_error_response(datagram: bytes) -> str:
    _, error_bytes = struct.unpack("!I64s", datagram)
    return error_bytes.rstrip(b'\x00').decode('utf-8')
#endregion

#region server-side build Functions
def build_say_response(channel_name: str, user_name: str, text: str) -> bytes:
    msg_type = 0
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
    user_bytes = user_name.encode('utf-8')[:32].ljust(32, b'\x00')
    text_bytes = text.encode('utf-8')[:64].ljust(64, b'\x00')
    return struct.pack("!I32s32s64s", msg_type, channel_bytes, user_bytes, text_bytes)

def build_list_response(channels_array: list) -> bytes:
    msg_type = 1
    channels_count = len(channels_array)
    datagram = struct.pack("!II", msg_type, channels_count) # Pack the message type
    
    for i in range(channels_count):
        channel_bytes = channels_array[i].encode('utf-8')[:32].ljust(32, b'\x00')
        datagram += channel_bytes
    return datagram

def build_who_response(channel_name: str, users_array: list) -> bytes:
    msg_type = 2
    users_count = len(users_array)
    channel_bytes = channel_name.encode('utf-8')[:32].ljust(32, b'\x00')
    datagram = struct.pack("!II32s", msg_type, users_count, channel_bytes)

    for i in range(users_count):
        user_bytes = users_array[i].encode('utf-8')[:32].ljust(32, b'\x00')
        datagramgram += user_bytes
    return datagram

def build_error_response(error_message: str) -> bytes:
    msg_type = 3
    error_bytes = error_message.encode('utf-8')[:64].ljust(64, b'\x00')
    return struct.pack("!I64s", msg_type, error_bytes)
#endregion

#region server-side parse Functions
def parse_login_request(datagram: bytes) -> str:
    _, username_bytes = struct.unpack("!I32s", datagram)
    return username_bytes.rstrip(b'\x00').decode('utf-8')

def parse_logout_request(datagram: bytes) -> None:
    # Logout has no payload
    return None

def parse_join_request(datagram: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", datagram)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')

def parse_leave_request(datagram: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", datagram)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')

def parse_say_request(datagram: bytes) -> tuple[str, str]:
    _, channel_bytes, text_bytes = struct.unpack("!I32s64s", datagram)
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')
    text = text_bytes.rstrip(b'\x00').decode('utf-8')
    return channel, text

def parse_list_request() -> None:
    # No payload
    return None

def parse_who_request(datagram: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", datagram)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')

def parse_keepalive_request(datagram: bytes) -> None:
    # No payload
    return None
#endregion
