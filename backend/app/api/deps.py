from fastapi import Query
from pydantic import BaseModel


class Pagination(BaseModel):
    limit: int = 50
    offset: int = 0


def pagination(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> Pagination:
    return Pagination(limit=limit, offset=offset)
