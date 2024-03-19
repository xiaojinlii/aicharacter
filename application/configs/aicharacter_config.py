

"""search 服务相关配置"""
SEARCH_SERVER_URL = "http://127.0.0.1:7862"
SEARCH_KB_NAME = "ai_character_{cid}"


LLM_MODELS_CONFIG = {
    "openai-api": {
        "model_name": "gpt-4",  # 由接口传入，不会使用这个
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "EMPTY",
    },
    "cyou-api": {
        "clientId": "a01a4923df7a43b39a4923df7a33b34c",
        "privateKey": "3cJB7EJH",
        "server_address": "http://10.1.9.87:8100",
        "api_url": "/cyouNeiOpenAi/api/chatGpt",
    },
}

PROMPT_TEMPLATE = """我希望你扮演角色{character_name}。
关于{character_name}的描述：{description}
关于{character_name}的其他信息：{definition}
我希望你像{character_name}那样使用他的语调、方式和词汇来回应和回答问题。
你要时刻保持在{character_name}的角色背景下，避免角色出戏，避免暴露你是ai的身份。
如果所问的问题不在{character_name}背景下，回复不了解。
如果所问的问题存在相关记忆，则优先根据记忆来回答，切忌过度的胡编乱造。"""

MEMORY_PROMPT_TEMPLATE = """问题：{question},
与此问题相关的记忆：{memory}
"""