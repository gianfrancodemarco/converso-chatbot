from typing import Optional, Type

import faker
from langchain.tools.base import StructuredTool
from pydantic import BaseModel

from converso_chatbot.clients import GetCalendarEventsPayload

fake = faker.Faker()


class GoogleCalendarRetrieverEvaluation(StructuredTool):
    name = "GoogleCalendarRetriever"
    description = """Useful to retrieve events from Google Calendar"""
    args_schema: Type[BaseModel] = GetCalendarEventsPayload
    return_direct = True
    chat_id: Optional[str] = None

    def _run(
        self,
        *args,
        **kwargs
    ) -> str:
        return "OK"
