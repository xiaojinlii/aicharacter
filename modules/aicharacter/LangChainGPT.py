from typing import List, Any, Callable

from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI

from application.settings import LLM_MODELS_CONFIG
from .langchain.cyou_chat import ChatCyou


def get_ChatOpenAI(
        model_name: str,
        temperature: float,
        max_tokens: int = None,
        streaming: bool = False,
        callbacks: List[Callable] = [],
        verbose: bool = True,
        **kwargs: Any,
) -> ChatOpenAI:
    if model_name == "cyou-api":
        configs = LLM_MODELS_CONFIG.get(model_name)
        model = ChatCyou(
            cyou_api_base=configs["server_address"],
            cyou_api_url=configs["api_url"],
            cyou_client_id=configs["clientId"],
            cyou_private_key=configs["privateKey"],
            temperature=temperature,
            verbose=verbose,
            callbacks=callbacks,
        )
    else:
        configs = LLM_MODELS_CONFIG.get("openai-api")
        model = ChatOpenAI(
            streaming=streaming,
            verbose=verbose,
            callbacks=callbacks,
            openai_api_key=configs["api_key"],
            openai_api_base=configs["api_base_url"],
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

    return model


class LangChainGPT:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0.7):
        self.chat = get_ChatOpenAI(model_name, temperature)
        self.messages = []

    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append(AIMessage(content=payload))

    def system_message(self, payload):
        self.messages.append(SystemMessage(content=payload))

    def user_message(self, payload):
        self.messages.append(HumanMessage(content=payload))

    def get_response(self):
        response = self.chat.invoke(self.messages)
        return response.content

    async def get_response_async(self):
        response = await self.chat.ainvoke(self.messages)
        return response.content

    def print_prompt(self):
        for message in self.messages:
            print(message)
