"""
FastAPI settings for project.
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 注意：不要在生产中打开调试运行!
DEBUG = False

####################
# PROJECT SETTINGS #
####################
TITLE = "AI Character"
DESCRIPTION = "基于 xiaoapi 的ai角色对话"
VERSION = "0.0.1"


############
# UVICORN #
############
# 监听主机IP，默认开放给本网络所有主机
HOST = "0.0.0.0"
# 监听端口
PORT = 9000
# 工作进程数
WORKERS = 1


##############
# MIDDLEWARE #
##############
# List of middleware to use. Order is important; in the request phase, these
# middleware will be applied in the order given, and in the response
# phase the middleware will be applied in reverse order.
MIDDLEWARES = [
    "xiaoapi.middleware.register_request_log_middleware",
]


#############
# DATABASES #
#############

# 数据库配置项
# 连接引擎官方文档：https://docs.sqlalchemy.org/en/20/core/engines.html
# mysql配置说明：mysql+asyncmy://数据库用户名:数据库密码@数据库地址:数据库端口/数据库名称，需安装asyncmy
# sqlite配置说明：sqlite+aiosqlite:///数据库路径，需安装aiosqlite
SQLALCHEMY_DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR}/db.sqlite3"

# 数据库迁移
# 会将MIGRATE_MODELS里所有的model迁移到数据库表结构
MIGRATE_MODELS = [
    "modules.aicharacter.models"
]


################
# AI Character #
################

SEARCH_SERVER_URL = "http://127.0.0.1:7862"
SEARCH_KB_NAME = "ai_character_{cid}"


LLM_MODELS_CONFIG = {
    "openai-api": {
        "model_name": "gpt-4",  # 由接口传入，不会使用这个
        "api_base_url": "https://api.openai.com/v1",
        "api_key": "EMPTY",
    },
}

PROMPT_TEMPLATE = """我希望你扮演角色{character_name}。
关于{character_name}的自我描述：{description}
关于{character_name}的背景故事以及说话方式：{definition}
我希望你像{character_name}那样使用他的语调、方式和词汇来回应和回答问题。
你要时刻保持在{character_name}的角色背景下，避免角色出戏，避免暴露你是ai的身份。
如果所问的问题不在{character_name}背景下，回复不了解。
如果所问的问题存在相关记忆，则优先根据记忆来回答，切忌过度的胡编乱造。"""

MEMORY_PROMPT_TEMPLATE = """问题：{question},
与此问题相关的记忆：{memory}
"""