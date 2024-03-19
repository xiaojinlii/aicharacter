from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import DalBase
from . import models, schemas


class CharacterDal(DalBase):
    def __init__(self, db: AsyncSession):
        super(CharacterDal, self).__init__()
        self.db = db
        self.model = models.CharacterModel
        self.schema = schemas.CharacterSimpleOut
