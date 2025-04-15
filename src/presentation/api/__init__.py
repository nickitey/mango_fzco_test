from .history_api_router import router as hist_router
from .entities_cruds import router as crud_router

__all__ = ("hist_router", "crud_router")
