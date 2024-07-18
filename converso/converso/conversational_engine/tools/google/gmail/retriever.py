import pickle
from typing import Optional, Type

from langchain.tools import BaseTool
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel

from converso.clients import GetEmailsPayload, GoogleClient, get_redis_client
from converso.constants import RedisKeys


class GmailRetriever(BaseTool):

    name = "GmailRetriever"
    description = """Useful to retrieve emails from Gmail"""
    args_schema: Type[BaseModel] = GetEmailsPayload

    return_direct = True
    chat_id: Optional[str] = None

    def _run(
        self,
        number_of_emails: Optional[int] = None,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""

        credentials = get_redis_client().hget(
            self.chat_id,
            RedisKeys.GOOGLE_CREDENTIALS.value
        )
        if not credentials:
            raise ValueError(
                "No Google credentials found. User must login first.")
        credentials = pickle.loads(credentials)

        google_client = GoogleClient(credentials)
        payload = GetEmailsPayload(
            number_of_emails=number_of_emails
        )
        return google_client.get_emails_html(payload)

    def get_tool_start_message(self, input: dict) -> str:
        payload = GetEmailsPayload(**input)
        return f"Retrieving the last {payload.number_of_emails} emails from Gmail"
