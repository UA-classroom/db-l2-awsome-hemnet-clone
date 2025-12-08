from typing import List, Optional
from fastapi import APIRouter, Depends, status, Response
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
from db import fetch_all, execute_returning
from helpers import get_db, handle_error, raise_if_not_found
from schemas import (
    UserCreate,
    SavedSearchCreate,
    SavedSearchUpdate,
    UserUpdate,
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
)

#########################################
#               GET                     #
#########################################


@router.get("/", tags=["users"])
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


@router.get("/{user_id}/saved-listings")
def user_saved_listings(
    user_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT sl.id,
               sl.created_at,
               l.id AS listing_id,
               l.title,
               l.list_price,
               ls.name AS status,
               loc.city,
               pt.name AS property_type
        FROM saved_listings sl
        JOIN listings l ON sl.listing_id = l.id
        JOIN listing_status ls ON l.status_id = ls.id
        JOIN listing_properties lp ON l.id = lp.listing_id
        JOIN properties p ON lp.property_id = p.id
        JOIN property_types pt ON p.property_type_id = pt.id
        JOIN locations loc ON p.location_id = loc.id
        WHERE sl.user_id = %s
        ORDER BY sl.created_at DESC
    """

    parameters: List = [user_id]

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}


@router.get("/{user_id}/searches")
def user_saved_searches(
    user_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT ss.id,
            ss.query,
            ss.location,
            ss.price_min,
            ss.price_max,
            ss.rooms_min,
            ss.rooms_max,
            ss.send_email,
            ss.created_at,
            ss.updated_at,
            array_agg(pt.name) AS property_types -- array_agg() för att eggregera pt.name till en array istället för en rad per property_type
        FROM saved_searches ss
        JOIN saved_search_property_type sspt
        ON sspt.saved_search_id = ss.id
        JOIN property_types pt
        ON pt.id = sspt.property_type_id
        WHERE user_id = %s
        GROUP BY ss.id
        ORDER BY created_at DESC
    """

    parameters: List = [user_id]

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}


#########################################
#                POST                   #
#########################################


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, connection=Depends(get_db)):
    query = """
        INSERT INTO users (email, password, first_name, last_name, phone, role_id, address_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, email, first_name, last_name, phone, role_id, address_id, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.email,
                payload.password,
                payload.first_name,
                payload.last_name,
                payload.phone,
                payload.role_id,
                payload.address_id,
            ),
        )

        return row
    except IntegrityError as exc:
        handle_error(exc, "User could not be created (email might already exist)")


@router.post(
    "/{user_id}/saved-listings",
    status_code=status.HTTP_201_CREATED,
)
def save_listing(user_id: int, listing_id: int, connection=Depends(get_db)):
    query = """
        INSERT INTO saved_listings (user_id, listing_id)
        VALUES (%s, %s)
        RETURNING id, user_id, listing_id, created_at
    """
    try:
        row = execute_returning(connection, query, (user_id, listing_id))

        return row
    except IntegrityError as exc:
        handle_error(exc, "Listing already saved or invalid reference")


@router.post("/{user_id}/searches", status_code=status.HTTP_201_CREATED)
def create_saved_search(
    user_id: int, payload: SavedSearchCreate, connection=Depends(get_db)
):
    query = """
        INSERT INTO saved_searches (user_id, query, location, price_min, price_max, rooms_min, rooms_max, send_email)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id, user_id, query, location, price_min, price_max, rooms_min, rooms_max, send_email, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                user_id,
                payload.query,
                payload.location,
                payload.price_min,
                payload.price_max,
                payload.rooms_min,
                payload.rooms_max,
                payload.send_email,
            ),
        )

        if row:
            for property_type in payload.property_types:
                type_row = execute_returning(
                    connection,
                    """
                        INSERT INTO saved_search_property_type(saved_search_id, property_type_id)
                        VALUES(%s, (SELECT id FROM property_types WHERE name = %s))
                        RETURNING *
                    """,
                    (row["id"], property_type.lower()),
                )

                raise_if_not_found(
                    type_row, f"Could not save property type {property_type}"
                )

        return row
    except IntegrityError as exc:
        handle_error(exc, "Could not create saved search")


#########################################
#               PUT                     #
#########################################


@router.put("/{user_id}")
def update_user(user_id: int, payload: UserUpdate, connection=Depends(get_db)):
    query = """
        UPDATE users
        SET email = COALESCE(%s, email),
            password = COALESCE(%s, password),
            first_name = COALESCE(%s, first_name),
            last_name = COALESCE(%s, last_name),
            phone = COALESCE(%s, phone),
            role_id = COALESCE(%s, role_id),
            address_id = COALESCE(%s, address_id),
            updated_at = NOW()
        WHERE id = %s
        RETURNING id, email, first_name, last_name, phone, role_id, address_id, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.email,
                payload.password,
                payload.first_name,
                payload.last_name,
                payload.phone,
                payload.role_id,
                payload.address_id,
                user_id,
            ),
        )

        return raise_if_not_found(row, "User")
    except IntegrityError as exc:
        handle_error(exc, "Could not update user")


@router.put("/{user_id}/searches/{search_id}")
def update_saved_search(
    user_id: int,
    search_id: int,
    payload: SavedSearchUpdate,
    connection=Depends(get_db),
):
    update_query = """
        UPDATE saved_searches
        SET query = COALESCE(%s, query),
            location = COALESCE(%s, location),
            price_min = COALESCE(%s, price_min),
            price_max = COALESCE(%s, price_max),
            rooms_min = COALESCE(%s, rooms_min),
            rooms_max = COALESCE(%s, rooms_max),
            send_email = COALESCE(%s, send_email),
            updated_at = NOW()
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, query, location, price_min, price_max, rooms_min, rooms_max, send_email, created_at, updated_at
    """
    property_type_insert = """
        INSERT INTO saved_search_property_type (saved_search_id, property_type_id)
        VALUES (%s, (SELECT id FROM property_types WHERE name = %s))
        RETURNING saved_search_id, property_type_id
    """
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    update_query,
                    (
                        payload.query,
                        payload.location,
                        payload.price_min,
                        payload.price_max,
                        payload.rooms_min,
                        payload.rooms_max,
                        payload.send_email,
                        search_id,
                        user_id,
                    ),
                )
                saved_search = raise_if_not_found(cursor.fetchone(), "Saved search")

                if payload.property_types is not None:
                    cursor.execute(
                        "DELETE FROM saved_search_property_type WHERE saved_search_id = %s",
                        (search_id,),
                    )
                    for property_type in payload.property_types:
                        cursor.execute(
                            property_type_insert, (search_id, property_type.lower())
                        )
                        raise_if_not_found(
                            cursor.fetchone(),
                            f"Could not save property type {property_type}",
                        )

        return saved_search
    except IntegrityError as exc:
        handle_error(exc, "Could not update saved search")


#########################################
#               DELETE                  #
#########################################


@router.delete(
    "/users/{user_id}/saved-listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
)
def delete_saved_listing(user_id: int, listing_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection,
        "DELETE FROM saved_listings WHERE user_id = %s AND listing_id = %s RETURNING id",
        (user_id, listing_id),
    )
    raise_if_not_found(deleted, "Favorite")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/users/{user_id}/searches/{search_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["users"],
)
def delete_saved_search(user_id: int, search_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection,
        "DELETE FROM saved_searches WHERE user_id = %s AND id = %s RETURNING id",
        (user_id, search_id),
    )

    raise_if_not_found(deleted, "Saved search")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
