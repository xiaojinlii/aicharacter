from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.model_base import BaseModel


class CharacterModel(BaseModel):
    __tablename__ = "character"
    __table_args__ = ({'comment': '角色表'})

    name: Mapped[str] = mapped_column(String(50), index=True, nullable=False, comment="姓名")
    description: Mapped[str] = mapped_column(String(1000), nullable=False, comment="描述")
    definition: Mapped[str] = mapped_column(String(1000), nullable=True, comment="定义")
