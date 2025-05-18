from dishka import make_async_container

from .container import AppProvider


def create_container():
    container = make_async_container(AppProvider())
    return container


__all__ = ("create_container",)
