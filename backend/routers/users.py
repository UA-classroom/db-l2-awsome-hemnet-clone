from fastapi import APIRouter, Depends
from typing import List, Optional
from ..helpers import get_db, fetch_all

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/users", tags=["users"])
def list_users(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT u.first_name, u.last_name, u.email, ur.name AS role
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id;
    """

    parameters: List = []

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}
