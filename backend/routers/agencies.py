from typing import Optional, List
from fastapi import APIRouter, Depends, status, Response
from psycopg2 import IntegrityError
from db import fetch_all, fetch_one, execute_returning
from helpers import (
    get_db,
    raise_if_not_found,
    handle_error,
    get_current_user,
)
from schemas import (
    AgencyCreate,
    AgencyUpdate,
    AgencyCreateOut,
    AgencyUpdateOut,
    AgencyDetailOut,
    AgenciesOut,
    User,
)


router = APIRouter(
    prefix="/agencies",
    tags=["agencies"],
)

#########################################
#               GET                     #
#########################################


@router.get("/", response_model=AgenciesOut)
def list_agencies(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT id,
               name,
               org_number,
               phone,
               website
        FROM agencies
        ORDER BY name
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


@router.get("/{agency_id}", response_model=AgencyDetailOut)
def agencies_datail(agency_id: int, connection=Depends(get_db)):
    query = """
        SELECT id,
               name,
               org_number,
               phone,
               website
        FROM agencies
        WHERE id = %s
    """

    row = fetch_one(connection, query, (agency_id,))
    return raise_if_not_found(row, "Agencies")


#########################################
#                POST                   #
#########################################


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AgencyCreateOut)
def create_agency(
    payload: AgencyCreate,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = """
        INSERT INTO agencies (name, org_number, phone, website, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id, name, org_number, phone, website, created_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (payload.name, payload.org_number, payload.phone, payload.website),
        )

        return row
    except IntegrityError as exc:
        handle_error(exc, "Could not create saved search")


#########################################
#               PUT                     #
#########################################


@router.put("/{agency_id}", response_model=AgencyUpdateOut)
def update_agency(
    agency_id: int,
    payload: AgencyUpdate,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = """
        UPDATE agencies
        SET name = COALESCE(%s, name),
            org_number = COALESCE(%s, org_number),
            phone = COALESCE(%s, phone),
            website = COALESCE(%s, website),
            updated_at = NOW()
        WHERE id = %s
        RETURNING id, name, org_number, phone, website, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.name,
                payload.org_number,
                payload.phone,
                payload.website,
                agency_id,
            ),
        )

        return raise_if_not_found(row, "Saved search")
    except IntegrityError as exc:
        handle_error(exc, "Could not update agency")


#########################################
#               DELETE                  #
#########################################


@router.delete(
    "/{agency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_agency(
    agency_id: int,
    connection=Depends(get_db),
    _: User = Depends(get_current_user),
):
    in_use = fetch_one(
        connection,
        "SELECT COUNT(*) AS count FROM agent_agencies WHERE agency_id = %s",
        (agency_id,),
    )

    if in_use and in_use["count"] > 0:
        execute_returning(
            connection, "DELETE FROM agent_agencies WHERE agency_id = %s", (agency_id,)
        )

    deleted = execute_returning(
        connection,
        "DELETE FROM agencies WHERE id = %s RETURNING id",
        (agency_id,),
    )

    raise_if_not_found(deleted, "Agency")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
