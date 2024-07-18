from enum import Enum


class MessageType(Enum):
    TEXT = "TEXT"
    TOOL_START = "TOOL_START"
    TOOL_END = "TOOL_END"
