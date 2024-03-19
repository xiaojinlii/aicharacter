import re
from typing import Optional, List

import tiktoken

from .schemas import History
from application.settings import SEARCH_KB_NAME

dialogue_bra_token = '「'
dialogue_ket_token = '」'

global _enc_model
_enc_model = None


def tokenizer(text):
    global _enc_model

    if _enc_model is None:
        _enc_model = tiktoken.get_encoding("cl100k_base")

    return len(_enc_model.encode(text))


def get_query_string(text, role):
    return f"{role}:{dialogue_bra_token}{text}{dialogue_ket_token}"


def response_postprocess(text, dialogue_bra_token='「', dialogue_ket_token='」'):
    lines = text.split('\n')
    new_lines = ""

    first_name = None

    for line in lines:
        line = line.strip(" ")
        match = re.match(r'^(.*?)[:：]' + dialogue_bra_token + r"(.*?)" + dialogue_ket_token + r"$", line)

        if match:
            curr_name = match.group(1)
            # print(curr_name)
            if first_name is None:
                first_name = curr_name
                new_lines += (match.group(2))
            else:
                if curr_name != first_name:
                    return first_name + ":" + dialogue_bra_token + new_lines + dialogue_ket_token
                else:
                    new_lines += (match.group(2))

        else:
            if first_name == None:
                return text
            else:
                return first_name + ":" + dialogue_bra_token + new_lines + dialogue_ket_token
    return first_name + ":" + dialogue_bra_token + new_lines + dialogue_ket_token


def add_history(llm, history: Optional[List[History]] = None, max_len_history=1200):
    if history is None or len(history) == 0:
        return

    print("sum_history_token---->")
    sum_history_token = 0
    flag = 0
    for h in reversed(history):
        print(h)
        current_count = tokenizer(h.content)
        sum_history_token += current_count
        if sum_history_token > max_len_history:
            break
        else:
            flag += 1

    if flag == 0:
        print('warning! no history added. the last dialogue is too long.')

    print(f"add----> flag:{flag}")
    for h in history[-flag:]:
        print(h)
        if h.role == "user":
            llm.user_message(h.content)
        elif h.role == "assistant":
            llm.ai_message(h.content)


def get_kb_name(cid):
    return SEARCH_KB_NAME.format(cid=cid)
