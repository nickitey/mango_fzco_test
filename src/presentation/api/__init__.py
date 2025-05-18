from .auth_router import router as auth_router
from .entities_cruds import router as crud_router
from .history_api_router import router as hist_router

__all__ = ("hist_router", "crud_router", "auth_router")
