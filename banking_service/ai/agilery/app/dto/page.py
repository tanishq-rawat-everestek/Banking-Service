"""
Generic pagination response schemas.
"""

from typing import Generic, TypeVar

from fastapi_camelcase import CamelModel

T = TypeVar("T")


class PageInfo(CamelModel):
    size: int
    number: int
    total_elements: int
    total_pages: int


class PageResponse(CamelModel, Generic[T]):
    content: list[T]
    page: PageInfo
