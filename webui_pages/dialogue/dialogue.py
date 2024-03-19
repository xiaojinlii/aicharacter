from typing import List, Dict

import streamlit as st

from streamlit_chatbox import *
import os

from webui_pages.api_request import ApiRequest, DEFAULT_BASE_URL
from webui_pages.utils import format_character_name

chat_box = ChatBox(
    assistant_avatar=os.path.join(
        "static/system",
        "chat_icon.png"
    )
)


def get_messages_history(history_len: int, content_in_expander: bool = False) -> List[Dict]:
    """
    返回消息历史。
    content_in_expander控制是否返回expander元素中的内容，一般导出的时候可以选上，传入LLM的history不需要
    """

    def filter(msg):
        content = [x for x in msg["elements"] if x._output_method in ["markdown", "text"]]
        if not content_in_expander:
            content = [x for x in content if not x._in_expander]
        content = [x.content for x in content]

        return {
            "role": msg["role"],
            "content": "\n\n".join(content),
        }

    return chat_box.filter_history(history_len=history_len, filter=filter)


def dialogue_page(api: ApiRequest):
    chat_input_placeholder = "请输入查询内容，换行请使用Shift+Enter。"

    def on_character_change():
        st.toast(f"已选择角色： {st.session_state.selected_character}")
        chat_box.reset_history()

    with st.sidebar:
        character_list = api.get_characters()
        character_dict = {c["name"]: c for c in character_list}
        character_names = [c["name"] for c in character_list]

        def format_selected_character(name: str) -> str:
            if character := character_dict.get(name):
                return format_character_name(character['id'], name)
            else:
                return name

        index = 0
        selected_character = st.selectbox(
            "请选择角色：",
            character_names,
            index=index,
            on_change=on_character_change,
            format_func=format_selected_character,
            key="selected_character",
        )

        if st.button("清空对话"):
            chat_box.reset_history()
            st.rerun()

    chat_box.output_messages()

    if query := st.chat_input(chat_input_placeholder, key="prompt"):
        if len(character_list) > 0:
            character = character_dict[selected_character]
            history = get_messages_history(10)
            chat_box.user_say(query)
            chat_box.ai_say(["对方正在输入 ..."])

            data = api.chat(character["id"], query, history)
            chat_box.update_msg(data, streaming=False)
        else:
            st.error("请先创建一个角色！")
