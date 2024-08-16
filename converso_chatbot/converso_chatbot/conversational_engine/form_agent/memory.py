import logging
import os
import pickle
from typing import Dict, Optional, Union

import redis
from langchain.memory import ConversationBufferWindowMemory
from langchain.memory.chat_memory import BaseChatMemory

from converso_chatbot.constants import RedisKeys
from converso.conversational_engine.form_agent.form_tool import AgentState, FormTool

logger = logging.getLogger(__name__)

HISTORY_LENGTH = os.getenv("HISTORY_LENGTH", 20)


class StoredAgentState:
    memory: Optional[BaseChatMemory]
    active_form_tool: Optional[Union[Dict, FormTool]]

    def __init__(
        self,
        memory: Optional[BaseChatMemory] = None,
        active_form_tool: Union[Dict, FormTool] = None
    ) -> None:

        if memory is None:
            memory = ConversationBufferWindowMemory(
                k=HISTORY_LENGTH,
                memory_key="history",
                human_prefix="Human",
                ai_prefix="Answer",
                input_key="messages",
                return_messages=True
            )

        self.memory = memory
        self.active_form_tool = active_form_tool

    def to_pickle(self):
        if self.active_form_tool:
            self.active_form_tool.form = self.active_form_tool.form.model_dump_json()
            self.active_form_tool.args_schema = self.active_form_tool.args_schema_
            self.active_form_tool.args_schema_ = None
        return pickle.dumps(self)

    @staticmethod
    def from_pickle(pickled: str):
        stored_agent_state = pickle.loads(pickled)
        if stored_agent_state.active_form_tool:
            stored_agent_state.active_form_tool.args_schema_ = stored_agent_state.active_form_tool.args_schema
            stored_agent_state.active_form_tool.init_state()
        return stored_agent_state


def get_stored_agent_state(
    redis_client: redis.Redis,
    chat_id: str
) -> StoredAgentState:
    stored_agent_state = redis_client.hget(
        chat_id,
        RedisKeys.AGENT_STATE.value
    )

    if stored_agent_state is not None:
        stored_agent_state: StoredAgentState = StoredAgentState.from_pickle(
            stored_agent_state)
        logger.info("Loaded agent state from redis")
    else:
        stored_agent_state = StoredAgentState()
    return stored_agent_state


def store_agent_state(
    redis_client: redis.Redis,
    chat_id: str,
    agent_state: AgentState
):
    stored_agent_state = StoredAgentState(
        memory=agent_state.memory,
        active_form_tool=agent_state.active_form_tool
    )

    redis_client.hset(
        chat_id,
        RedisKeys.AGENT_STATE.value,
        stored_agent_state.to_pickle()
    )
