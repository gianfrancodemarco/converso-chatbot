
import json
import logging
import pprint
from textwrap import dedent
from typing import Any

from fastapi.responses import JSONResponse

from converso.clients import (RabbitMQProducer, get_rabbitmq_producer,
                              get_redis_client)
from converso.clients.rabbitmq import RabbitMQProducer
from converso.constants import MessageQueues, MessageType
from converso.constants.message_queues import MessageQueues
from converso.constants.message_type import MessageType
from converso.conversational_engine.form_agent import (FormAgentExecutor,
                                                       FormTool,
                                                       get_stored_agent_state,
                                                       store_agent_state)
from converso.conversational_engine.tool_callback_handler import \
    ToolCallbackHandler
from converso.conversational_engine.tools import *
from converso.models.chat_payload import ChatPayload

pp = pprint.PrettyPrinter(indent=4)

logger = logging.getLogger(__name__)

rabbitmq_producer = get_rabbitmq_producer()
redis_client = get_redis_client()


async def process_message(data: dict) -> None:

    data: ChatPayload = ChatPayload.model_validate(data)

    chat_id = data.chat_id
    tools = [
        GoogleSearch(),
        GoogleCalendarCreator(chat_id=chat_id),
        GoogleCalendarRetriever(chat_id=chat_id),
        GmailRetriever(chat_id=chat_id),
        GmailSender(chat_id=chat_id),
        OnlinePurchase(),
        PythonCodeInterpreter()
    ]

    stored_agent_state = get_stored_agent_state(redis_client, data.chat_id)

    inputs = {
        "input": data.content,
        "chat_history": [*stored_agent_state.memory.buffer],
        "intermediate_steps": [],
        "active_form_tool": stored_agent_state.active_form_tool
    }

    tool_callback_handler = ToolCallbackHandler(
        chat_id=chat_id,
        tools=tools,
        rabbitmq_producer=rabbitmq_producer,
        queue=MessageQueues.converso_OUT.value
    )

    graph = FormAgentExecutor(
        tools=tools,
        on_tool_start=tool_callback_handler.on_tool_start,
        on_tool_end=tool_callback_handler.on_tool_end
    )

    logger.info(dedent(f"""
        ---
        Executing graph with inputs: {inputs}"
        ---
    """))

    for output in graph.app.stream(inputs, config={"recursion_limit": 25}):
        for key, value in output.items():
            pass

    answer = graph.parse_output(output)

    # Prepare input and memory
    stored_agent_state.memory.save_context(
        inputs={"messages": data.content},
        outputs={"output": answer}
    )
    stored_agent_state.active_form_tool = value["active_form_tool"]

    store_agent_state(redis_client, data.chat_id, stored_agent_state)
    publish_answer(rabbitmq_producer, data.chat_id, answer)


def publish_answer(
        rabbitmq_client: RabbitMQProducer,
        chat_id: str,
        answer: str):
    rabbitmq_client.publish(
        queue=MessageQueues.converso_OUT.value,
        message=json.dumps({
            "type": MessageType.TEXT.value,
            "chat_id": chat_id,
            "content": answer
        })
    )
    logger.info("Published answer to RabbitMQ")
