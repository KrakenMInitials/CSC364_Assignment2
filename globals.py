from collections import namedtuple
import ctypes

SocketAddress = tuple[str, int]
UserAddress = namedtuple("UserAddress", ["username", "port"])
User = namedtuple("User", ["username", "user_address", "last_activity"])
uint32 = ctypes.c_uint32
