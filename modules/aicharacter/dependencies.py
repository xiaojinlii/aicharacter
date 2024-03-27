from fastapi import Depends, Query
from xiaoapi_sqlalchemy import Paging, QueryParams


class CharacterParams(QueryParams):
    """
    列表分页
    """

    def __init__(
            self,
            name: str | None = Query(None, title="角色名称"),
            params: Paging = Depends()
    ):
        super().__init__(params)
        self.name = ("like", name)
