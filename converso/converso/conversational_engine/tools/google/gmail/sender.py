import pickle
import textwrap
from typing import Dict, Optional, Type, Union

from pydantic import BaseModel

from converso.clients import GoogleClient, SendEmailPayload, get_redis_client
from converso.constants import RedisKeys
from converso.constants.redis_keys import RedisKeys
from converso.conversational_engine.form_agent import FormTool, FormToolState


class GmailSender(FormTool):

    name = "GmailSender"
    description = """Useful to send emails from Gmail"""
    args_schema: Type[BaseModel] = SendEmailPayload

    chat_id: Optional[str] = None

    def _run_when_complete(
        self,
        to: str,
        subject: str,
        body: str
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
        payload = SendEmailPayload(
            body=body,
            subject=subject,
            to=to
        )
        return google_client.send_email(payload)

    def get_tool_start_message(self, input: Union[Dict, str]) -> str:
        base_message = super().get_tool_start_message(input)
        if self.state in (FormToolState.ACTIVE, FormToolState.FILLED):
            payload = self.args_schema(**input)
            return f"{base_message}\n" +\
                textwrap.dedent(f"""
                    Subject: {payload.subject}
                    To: {payload.to}
                    Body: {payload.body}
                """)

        return base_message
