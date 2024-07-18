from pydantic import BaseModel

# TODO: Change in MessageQueueInPayload and MessageQueueOutPayload


class ChatPayload(BaseModel):
    chat_id: str
    content: str
