from enum import Enum

class ProtocolType(Enum):
    SERVER = 0
    CLIENT = 1
    LISTEN = 2
    BROADCAST = 3