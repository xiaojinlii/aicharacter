from fastapi import FastAPI

# from modules.quickstart.routes import router as quickstart_router
from modules.aicharacter.routes import router as aicharacter_router


def register_routes(app: FastAPI):
    """
    注册路由
    """

    # app.include_router(quickstart_router, prefix="/quickstart", tags=["快速开始"])
    app.include_router(aicharacter_router, prefix="/character", tags=["角色管理"])
