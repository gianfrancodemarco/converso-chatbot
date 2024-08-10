import pickle
import textwrap
from datetime import datetime
from typing import Optional, Type

from pydantic import BaseModel

from converso_chatbot.clients import (GetCalendarEventsPayload, GoogleClient,
                              get_redis_client)
from converso_chatbot.constants import RedisKeys
from converso.conversational_engine.form_agent.form_tool import (
    FormTool, FormToolState)


class GoogleCalendarRetriever(FormTool):

    name = "GoogleCalendarRetriever"
    description = """Useful to retrieve events from Google Calendar"""
    args_schema: Type[BaseModel] = GetCalendarEventsPayload

    return_direct = True
    skip_confirm = True
    chat_id: Optional[str] = None

    def _run_when_complete(
        self,
        start: datetime,
        end: datetime
    ) -> str:
        credentials = get_redis_client().hget(
            self.chat_id,
            RedisKeys.GOOGLE_CREDENTIALS.value
        )
        google_client = GoogleClient(pickle.loads(credentials))
        payload = GetCalendarEventsPayload(
            start=start,
            end=end,
        )
        return google_client.get_calendar_events_html(payload)

    def get_tool_start_message(self, input: dict) -> str:
        base_message = super().get_tool_start_message(input)
        if self.state in (FormToolState.ACTIVE, FormToolState.FILLED):
            payload = GetCalendarEventsPayload(**input)

            return f"{base_message}\n" +\
                textwrap.dedent(f"""
                    Start: {payload.start}
                    End: {payload.end}
                """)

        return base_message
