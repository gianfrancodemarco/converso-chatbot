from typing import Type

from langchain.tools import StructuredTool
from pydantic import BaseModel

from converso_chatbot.conversational_engine.tools.online_purchase import \
    OnlinePurchasePayload


class OnlinePurchaseEvaluation(StructuredTool):
    name = "OnlinePurchase"
    description = """Purchase an item from an online store"""
    args_schema: Type[BaseModel] = OnlinePurchasePayload

    def _run(
        self,
        *args,
        **kwargs
    ) -> str:
        return "OK"
