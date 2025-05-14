import struct

#region client-side build Functions
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
#endregion

#region client-side parse Functions
def parse_say_response(data: bytes) -> tuple[str, str, str]:
    _, channel_bytes, user_bytes, text_bytes = struct.unpack("!I32s32s64s", data)
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')
    user = user_bytes.rstrip(b'\x00').decode('utf-8')
    text = text_bytes.rstrip(b'\x00').decode('utf-8')
    return channel, user, text

def parse_list_response(data: bytes) -> list[str]:
    _, count = struct.unpack("!II", data[:8])
    channels = []
    offset = 8
    for _ in range(count):
        (ch_bytes,) = struct.unpack("!32s", data[offset:offset+32])
        channels.append(ch_bytes.rstrip(b'\x00').decode('utf-8'))
        offset += 32
    return channels

def parse_who_response(data: bytes) -> tuple[str, list[str]]:
    _, count = struct.unpack("!II", data[:8])
    channel_bytes = struct.unpack("!32s", data[8:40])[0]
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')

    users = []
    offset = 40
    for _ in range(count):
        (user_bytes,) = struct.unpack("!32s", data[offset:offset+32])
        users.append(user_bytes.rstrip(b'\x00').decode('utf-8'))
        offset += 32
    return channel, users

def parse_error_response(data: bytes) -> str:
    _, error_bytes = struct.unpack("!I64s", data)
    return error_bytes.rstrip(b'\x00').decode('utf-8')
#endregion

#region server-side build Functions
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
#endregion

#region server-side parse Functions
def parse_login(data: bytes) -> str:
    _, username_bytes = struct.unpack("!I32s", data)
    return username_bytes.rstrip(b'\x00').decode('utf-8')


def parse_logout(data: bytes) -> None:
    # Logout has no payload
    return None


def parse_join(data: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", data)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')


def parse_leave(data: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", data)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')


def parse_say(data: bytes) -> tuple[str, str]:
    _, channel_bytes, text_bytes = struct.unpack("!I32s64s", data)
    channel = channel_bytes.rstrip(b'\x00').decode('utf-8')
    text = text_bytes.rstrip(b'\x00').decode('utf-8')
    return channel, text

def parse_list(data: bytes) -> None:
    # No payload
    return None


def parse_who(data: bytes) -> str:
    _, channel_bytes = struct.unpack("!I32s", data)
    return channel_bytes.rstrip(b'\x00').decode('utf-8')


def parse_keepalive(data: bytes) -> None:
    # No payload
    return None
#endregion
