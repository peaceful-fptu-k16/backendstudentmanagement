from typing import Generic, TypeVar, List, Optional
from fastapi import Query
from sqlmodel import Session, select, func
from math import ceil

T = TypeVar('T')

class PaginationParams:
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

class PaginatedResult(Generic[T]):
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ):
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        self.total_pages = ceil(total / page_size) if page_size > 0 else 0
        self.has_next = page < self.total_pages
        self.has_prev = page > 1

def paginate(
    db: Session,
    query,
    page: int,
    page_size: int
) -> PaginatedResult:
    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()
    offset = (page - 1) * page_size
    paginated_query = query.offset(offset).limit(page_size)
    items = db.exec(paginated_query).all()
    return PaginatedResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
