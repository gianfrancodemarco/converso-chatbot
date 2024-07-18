
import json
from typing import Any

from converso.clients import RabbitMQProducer
from converso.clients.rabbitmq import RabbitMQProducer
from converso.constants import MessageQueues, MessageType
from converso.constants.message_queues import MessageQueues
from converso.constants.message_type import MessageType
from converso.conversational_engine.form_agent import FormTool


class ToolCallbackHandler:

    def __init__(
        self,
        chat_id: str,
        tools: list = None,
        rabbitmq_producer: RabbitMQProducer = None,
        queue: MessageQueues = None
    ) -> None:
        self.chat_id = chat_id
        self.tools = tools
        self.rabbitmq_client = rabbitmq_producer
        self.queue = queue

    def on_tool_start(
        self,
        tool: FormTool,
        tool_input: str
    ) -> Any:
        """Run when tool starts running."""
        if not self.rabbitmq_client:
            return

        try:
            tool_start_message = tool.get_tool_start_message(tool_input)
        except BaseException:
            tool_start_message = f"{tool.name}: {tool_input}"

        self.rabbitmq_client.publish(
            queue=self.queue,
            message=json.dumps({
                "chat_id": self.chat_id,
                "type": MessageType.TOOL_START.value,
                "content": tool_start_message
            })
        )

    def on_tool_end(
        self,
        tool: FormTool,
        tool_output: str
    ) -> Any:
        """Run when tool ends running."""

        if not self.rabbitmq_client:
            return

        self.rabbitmq_client.publish(
            queue=self.queue,
            message=json.dumps({
                "chat_id": self.chat_id,
                "type": MessageType.TOOL_END.value,
                "content": tool_output
            })
        )
