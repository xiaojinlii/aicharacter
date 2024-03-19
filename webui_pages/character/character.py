import streamlit as st
from st_aggrid import AgGrid, JsCode
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pandas as pd
from typing import Literal, Dict, Tuple, List

from application.settings import SEARCH_SERVER_URL, SEARCH_KB_NAME
from webui_pages.api_request import ApiRequest, check_error_msg, check_success_msg
from webui_pages.utils import format_character_name

api_search = ApiRequest(base_url=SEARCH_SERVER_URL)


def config_aggrid(
        df: pd.DataFrame,
        columns: Dict[Tuple[str, str], Dict] = {},
        selection_mode: Literal["single", "multiple", "disabled"] = "single",
        use_checkbox: bool = False,
) -> GridOptionsBuilder:
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("No", width=40)
    for (col, header), kw in columns.items():
        gb.configure_column(col, header, wrapHeaderText=True, **kw)
    gb.configure_selection(
        selection_mode=selection_mode,
        use_checkbox=use_checkbox,
        pre_selected_rows=st.session_state.get("selected_rows", [0]),
    )
    gb.configure_pagination(
        enabled=True,
        paginationAutoPageSize=False,
        paginationPageSize=10
    )
    return gb


def character_page(api: ApiRequest):
    character_list = api.get_characters()
    character_dict = {c["name"]: c for c in character_list}
    character_names = [c["name"] for c in character_list]

    if "selected_character_name" in st.session_state and st.session_state["selected_character_name"] in character_names:
        selected_character_index = character_names.index(st.session_state["selected_character_name"])
    else:
        selected_character_index = 0

    def format_selected_character(name: str) -> str:
        if character := character_dict.get(name):
            return format_character_name(character['id'], name)
        else:
            return name

    selected_character = st.selectbox(
        "请选择或新建角色：",
        character_names + ["新建角色"],
        format_func=format_selected_character,
        index=selected_character_index
    )

    if selected_character == "新建角色":
        with st.form("新建角色"):
            character_name = st.text_input(
                "角色名称",
                placeholder="例如 乔峰",
                key="character_name",
            )
            character_description = st.text_area(
                "角色描述",
                placeholder="你的角色会如何描述自己？",
                key="character_description",
                max_chars=1000,
            )

            character_definition = st.text_area(
                "角色定义",
                placeholder="你的角色的背景故事是什么？你希望它如何说话或行动？",
                key="character_definition",
                max_chars=1000,
            )

            submit_create_kb = st.form_submit_button(
                "新建",
                use_container_width=True,
            )

        if submit_create_kb:
            if not character_name or not character_name.strip():
                st.error(f"知角色名称不能为空！")
            else:
                ret = api.create_character(
                    name=character_name,
                    description=character_description,
                    definition=character_definition
                )
                st.toast(ret.get("message", " "))
                st.session_state["selected_character_name"] = character_name
                st.rerun()

    elif selected_character:
        character = character_dict[selected_character]

        character_description = st.text_area(
            "角色描述",
            value=character["description"],
            placeholder="你的角色会如何描述自己？",
            key="character_description",
            max_chars=1000,
        )

        character_definition = st.text_area(
            "角色定义",
            value=character["definition"],
            placeholder="你的角色的背景故事是什么？你希望它如何说话或行动？",
            key="character_definition",
            max_chars=1000,
        )

        cols = st.columns(2)
        st.write()
        if cols[0].button(
                "更新角色信息",
                disabled=character_description == character['description'] and character_definition == character[
                    'definition'],
                use_container_width=True
        ):
            ret = api.update_character(character["id"], character_description, character_definition)
            st.toast(ret.get("message", " "))
            st.rerun()

        if cols[1].button("删除角色", type="primary", use_container_width=True):
            ret = api.del_character(character["id"])
            st.toast(ret.get("message", " "))
            st.rerun()

        st.divider()

        kb_name = SEARCH_KB_NAME.format(cid=character["id"])
        # 知识库详情
        doc_details = pd.DataFrame(api_search.list_kb_file_details(kb_name))
        if not len(doc_details):
            st.info(f"记忆库中暂无文件，请上传记忆文件")
        else:
            st.info(f"记忆库中已有文件:")
            doc_details.drop(columns=["kb_name"], inplace=True)
            doc_details = doc_details[[
                "No", "file_name", "docs_count", "document_loader", "text_splitter",
            ]]
            gb = config_aggrid(
                doc_details,
                {
                    ("No", "序号"): {},
                    ("file_name", "文档名称"): {},
                    # ("file_ext", "文档类型"): {},
                    # ("file_version", "文档版本"): {},
                    ("document_loader", "文档加载器"): {},
                    ("docs_count", "文档数量"): {},
                    ("text_splitter", "分词器"): {},
                    # ("create_time", "创建时间"): {},
                },
                "multiple",
            )

            doc_grid = AgGrid(
                doc_details,
                gb.build(),
                columns_auto_size_mode="FIT_CONTENTS",
                theme="alpine",
                custom_css={
                    "#gridToolBar": {"display": "none"},
                },
                allow_unsafe_jscode=True,
                enable_enterprise_modules=False
            )

            selected_rows = doc_grid.get("selected_rows", [])

            if st.button(
                    "删除选中文档",
                    type="primary",
                    use_container_width=True,
            ):
                file_names = [row["file_name"] for row in selected_rows]
                api_search.delete_files(kb_name, file_names=file_names, delete_content=True)
                st.rerun()

        # 上传文件
        files = st.file_uploader("选择记忆文件：", accept_multiple_files=True)

        if st.button("上传记忆文件", disabled=len(files) == 0):
            pass
            ret = api_search.upload_files(
                files,
                knowledge_base_name=kb_name,
                override=True,
            )
            if msg := check_success_msg(ret):
                st.toast(msg, icon="✔")
            elif msg := check_error_msg(ret):
                st.toast(msg, icon="✖")
            st.rerun()
