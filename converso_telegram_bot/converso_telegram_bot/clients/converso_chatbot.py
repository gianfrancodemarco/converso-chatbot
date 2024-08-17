import os

import requests


class ConversoChatbotClient:

    def __init__(self) -> None:
        self.HOST = os.environ.get('CONVERSO_URL', 'localhost:8000')
        self.REST_URL = f"http://{self.HOST}"

    def chat(
        self,
        chat_id: str,
        message: str
    ) -> str:
        response = requests.post(
            f"{self.REST_URL}/chat",
            json={"chat_id": chat_id, "question": message},
        )
        return response.json()

    def reset_conversation(
        self,
        chat_id: str
    ) -> None:
        requests.delete(f"{self.REST_URL}/conversations/{chat_id}")

    def login_to_google(
        self,
        chat_id: str
    ) -> str:
        response = requests.post(f"{self.REST_URL}/google/login/{chat_id}")
        return response.json()["content"]
