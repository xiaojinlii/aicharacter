from typing import List

import aiohttp
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.settings import SEARCH_SERVER_URL, SEARCH_KB_NAME, PROMPT_TEMPLATE, MEMORY_PROMPT_TEMPLATE
from xiaoapi.core import CustomException, logger
from xiaoapi_sqlalchemy import IdList
from . import schemas, crud
from xiaoapi_sqlalchemy.database import db_getter
from xiaoapi.response import SuccessResponse
from .LangChainGPT import LangChainGPT
from .utils import add_history, response_postprocess, get_kb_name
from .dependencies import CharacterParams


router = APIRouter()


@router.get("/characters", summary="获取角色列表")
async def get_characters(
        params: CharacterParams = Depends(),
        db: AsyncSession = Depends(db_getter)
):
    datas, count = await crud.CharacterDal(db).get_datas(**params.dict(), v_return_count=True)
    return SuccessResponse(datas, count=count)


@router.get("/characters/{data_id}", summary="获取角色信息")
async def get_character(
        data_id: int,
        db: AsyncSession = Depends(db_getter)
):
    return SuccessResponse(await crud.CharacterDal(db).get_data(data_id, v_schema=schemas.CharacterSimpleOut))


@router.post("/characters", summary="创建角色信息")
async def create_characters(
        character: schemas.Character,
        db: AsyncSession = Depends(db_getter)
):
    new_character = await crud.CharacterDal(db).create_data(data=character)

    url = f"{SEARCH_SERVER_URL}/knowledge_base/create_knowledge_base"
    data = {
        "knowledge_base_name": get_kb_name(new_character['id']),
        "vector_store_type": "es",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status != 200:
                raise CustomException(f"Error from create_knowledge_base api response: {await response.text()}")
            ret = await response.json()
            if ret["code"] == 400:
                raise CustomException(ret["message"])

    return SuccessResponse(msg="角色创建成功", data=new_character)


@router.delete("/characters", summary="批量删除角色")
async def delete_characters(
        ids: IdList = Depends(),
        db: AsyncSession = Depends(db_getter)
):
    await crud.CharacterDal(db).delete_datas(ids.ids)

    url = f"{SEARCH_SERVER_URL}/knowledge_base/delete_knowledge_base"
    for cid in ids.ids:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=get_kb_name(cid)) as response:
                if response.status != 200:
                    raise CustomException(f"Error from delete_knowledge_base api response: {await response.text()}")
                ret = await response.json()
                if ret["code"] == 400:
                    raise CustomException(ret["message"])

    return SuccessResponse(msg="删除成功")


@router.put("/characters/{data_id}", summary="更新角色信息")
async def put_characters(
        data_id: int,
        data: schemas.CharacterUpdateInfo,
        db: AsyncSession = Depends(db_getter)
):

    return SuccessResponse(await crud.CharacterDal(db).put_data(data_id, data), msg="角色信息更新成功")


@router.post("/chat/{data_id}", summary="与角色对话")
async def chat(
        data_id: int,
        chat_data: schemas.ChatIn,
        db: AsyncSession = Depends(db_getter)
):
    character = await crud.CharacterDal(db).get_data(data_id)

    docs = await search_docs(query=chat_data.text, knowledge_base_name=get_kb_name(data_id))

    llm = LangChainGPT(model_name="cyou-api")

    system_prompt = PROMPT_TEMPLATE.format(character_name=character.name, description=character.description, definition=character.definition)
    llm.system_message(system_prompt)

    if chat_data.history:
        add_history(llm, chat_data.history)

    user_prompt = chat_data.text
    if len(docs) > 0:
        user_prompt = MEMORY_PROMPT_TEMPLATE.format(question=chat_data.text, memory=docs)
    llm.user_message(user_prompt)

    # llm.print_prompt()

    response_raw = await llm.get_response_async()
    response = response_postprocess(response_raw)

    return SuccessResponse(response)


async def search_docs(
        query: str = "",
        knowledge_base_name: str = "",
        top_k: int = 3,
        score_threshold: float = 2,
) -> List[str]:

    data = {
        "query": query,
        "knowledge_base_name": knowledge_base_name,
        "top_k": top_k,
        "score_threshold": score_threshold,
    }

    url = f"{SEARCH_SERVER_URL}/knowledge_base/search_docs"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            if response.status != 200:
                raise CustomException(f"Error from search_docs api response: {await response.text()}")
            ret = await response.json()

    result = [d["page_content"] for d in ret]
    logger.info(f"search_docs:{result}")
    return result
