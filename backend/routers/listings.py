from typing import Optional, List
from fastapi import APIRouter, Depends, status, Response
from psycopg2 import IntegrityError
from psycopg2.extras import RealDictCursor
from db import fetch_all, fetch_one, execute_returning
from helpers import (
    get_db,
    raise_if_not_found,
    handle_error,
    get_current_user,
)
from schemas import (
    ListingCreate,
    ListingMediaCreate,
    OpenHouseCreate,
    ListingUpdate,
    User,
)


router = APIRouter(
    prefix="/listings",
    tags=["listings"],
)

#########################################
#               GET                     #
#########################################


@router.get("/autocomplete")
def autocomplete_headings(search_term: str, connection=Depends(get_db)):
    query = """
        SELECT DISTINCT l.title
        FROM listings l
        JOIN listing_properties lp ON l.id = lp.listing_id
        JOIN properties p ON lp.property_id = p.id
        JOIN locations loc ON p.location_id = loc.id
        WHERE l.title ILIKE %s OR loc.city ILIKE %s
        ORDER BY l.title
        LIMIT 10
    """

    like_term = f"{search_term}%"
    rows = fetch_all(connection, query, (like_term, like_term))
    return {"count": len(rows), "items": rows}


@router.get("/")
def list_listings(
    free_text_search: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rooms: Optional[float] = None,
    max_rooms: Optional[float] = None,
    property_type: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    status_name: Optional[str] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT l.id,
               l.title,
               ls.name AS status,
               l.list_price,
               pt.name AS property_type,
               p.rooms,
               p.living_area_sqm,
               loc.city,
               lm.url AS image
        FROM listings l
        JOIN listing_status ls ON l.status_id = ls.id
        JOIN listing_properties lp ON l.id = lp.listing_id
        LEFT JOIN listing_media lm ON l.id = lm.listing_id 
            AND lm.media_type_id = 1
            AND lm.id = (
                SELECT MIN(id) 
                FROM listing_media 
                WHERE listing_id = l.id AND media_type_id = 1
            )
        JOIN properties p ON lp.property_id = p.id
        JOIN property_types pt ON p.property_type_id = pt.id
        JOIN locations loc ON p.location_id = loc.id
    """
    conditions: List[str] = []
    parameters: List = []

    if free_text_search:
        conditions.append("(l.title ILIKE %s OR loc.city ILIKE %s)")
        search_term = f"{free_text_search}%"
        parameters.append(search_term)
        parameters.append(search_term)
    if status_name:
        conditions.append("ls.name = %s")
        parameters.append(status_name)
    if city:
        conditions.append("loc.city ILIKE %s")
        parameters.append(f"%{city}%")
    if min_price is not None:
        conditions.append("l.list_price >= %s")
        parameters.append(min_price)
    if max_price is not None:
        conditions.append("l.list_price <= %s")
        parameters.append(max_price)
    if min_rooms is not None:
        conditions.append("p.rooms >= %s")
        parameters.append(min_rooms)
    if max_rooms is not None:
        conditions.append("p.rooms <= %s")
        parameters.append(max_rooms)
    if property_type is not None:
        types = [t.strip() for t in property_type.split(",")]
        placeholders = ", ".join(["%s"] * len(types))
        conditions.append(f"pt.name IN ({placeholders})")
        parameters.extend(types)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY l.id"

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}


@router.get("/{listing_id}")
def listing_detail(listing_id: int, connection=Depends(get_db)):
    query = """
        SELECT l.id,
               l.title,
               l.description,
               ls.name AS status,
               l.list_price,
               l.price_type_id,
               l.published_at,
               l.expires_at,
               l.external_ref,
               pt.name AS property_type,
               t.name AS tenure,
               p.rooms,
               p.living_area_sqm,
               p.plot_area_sqm,
               p.energy_class,
               p.year_built,
               loc.street_address,
               loc.postal_code,
               loc.city,
               loc.municipality,
               u.first_name || ' ' || u.last_name AS agent_name,
               u.phone AS agent_phone,
               ag.name AS agency
        FROM listings l
        JOIN listing_status ls ON l.status_id = ls.id
        JOIN listing_properties lp ON l.id = lp.listing_id
        JOIN properties p ON lp.property_id = p.id
        JOIN property_types pt ON p.property_type_id = pt.id
        JOIN tenures t ON p.tenure_id = t.id
        JOIN locations loc ON p.location_id = loc.id
        JOIN listing_agents la ON l.id = la.listing_id
        JOIN agents a ON la.agent_id = a.id
        JOIN users u ON a.user_id = u.id
        LEFT JOIN agent_agencies aa ON a.id = aa.agent_id
        LEFT JOIN agencies ag ON aa.agency_id = ag.id
        WHERE l.id = %s
        LIMIT 1
    """
    row = fetch_one(connection, query, (listing_id,))
    return raise_if_not_found(row, "Listing")


@router.get("/{listing_id}/media")
def listing_media(
    listing_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT id, media_type_id, url, caption, position, updated_at
        FROM listing_media
        WHERE listing_id = %s
        ORDER BY position NULLS LAST, id
    """

    parameters: List = [listing_id]

    if limit is not None:
        query += " LIMIT %s"
        parameters.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        parameters.append(offset)

    rows = fetch_all(connection, query, parameters)
    return {"count": len(rows), "items": rows}


@router.get("/{listing_id}/open-houses")
def listing_open_houses(
    listing_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT oh.id,
               oh.starts_at,
               oh.ends_at,
               oht.name AS type,
               oh.note
        FROM open_houses oh
        JOIN open_house_types oht ON oh.type_id = oht.id
        WHERE oh.listing_id = %s
        ORDER BY oh.starts_at
    """

    parameters: List = [listing_id]

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


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    description="Add a property first to get the property ID",
    tags=["listings"],
)
def create_listing(payload: ListingCreate, connection=Depends(get_db)):
    listing_query = """
        INSERT INTO listings (
            agent_id, title, description, status_id, list_price, price_type_id,
            published_at, expires_at, external_ref
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    link_query = "INSERT INTO listing_properties (property_id, listing_id) VALUES (%s, %s) RETURNING listing_id, property_id"
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    listing_query,
                    (
                        payload.agent_id,
                        payload.title,
                        payload.description,
                        payload.status_id,
                        payload.list_price,
                        payload.price_type_id,
                        payload.published_at,
                        payload.expires_at,
                        payload.external_ref,
                    ),
                )
                listing = cursor.fetchone()
                cursor.execute(link_query, (payload.property_id, listing["id"]))
                cursor.fetchone()

                return listing
    except IntegrityError as exc:
        handle_error(
            exc,
            "Could not create listing (check agent, status, or property references)",
        )


@router.post(
    "/{listing_id}/media",
    status_code=status.HTTP_201_CREATED,
    tags=["listings"],
)
def add_listing_media(
    listing_id: int, payload: ListingMediaCreate, connection=Depends(get_db)
):
    query = """
        INSERT INTO listing_media (listing_id, media_type_id, url, caption, position)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                listing_id,
                payload.media_type_id,
                payload.url,
                payload.caption,
                payload.position,
            ),
        )

        return row
    except IntegrityError as exc:
        handle_error(exc, "Could not add listing media")


@router.post(
    "/{listing_id}/open-houses",
    status_code=status.HTTP_201_CREATED,
    tags=["listings"],
)
def add_open_house(
    listing_id: int, payload: OpenHouseCreate, connection=Depends(get_db)
):
    query = """
        INSERT INTO open_houses (listing_id, starts_at, ends_at, type_id, note)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                listing_id,
                payload.starts_at,
                payload.ends_at,
                payload.type_id,
                payload.note,
            ),
        )

        return row
    except IntegrityError as exc:
        handle_error(exc, "Could not create open house entry")


#########################################
#               PUT                     #
#########################################


@router.put("/{listing_id}")
def update_listing(listing_id: int, payload: ListingUpdate, connection=Depends(get_db)):
    listing_query = """
        UPDATE listings
        SET agent_id = COALESCE(%s, agent_id),
            title = %s,
            description = COALESCE(%s, description),
            status_id = COALESCE(%s, status_id),
            list_price = COALESCE(%s, list_price),
            price_type_id = COALESCE(%s, price_type_id),
            published_at = COALESCE(%s, published_at),
            expires_at = COALESCE(%s, expires_at),
            external_ref = COALESCE(%s, external_ref),
            updated_at = NOW()
        WHERE id = %s
        RETURNING *
    """
    link_query = """
        UPDATE listing_properties SET property_id = COALESCE(%s, property_id)
        WHERE listing_id = %s
    """
    try:
        with connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    listing_query,
                    (
                        payload.agent_id,
                        payload.title,
                        payload.description,
                        payload.status_id,
                        payload.list_price,
                        payload.price_type_id,
                        payload.published_at,
                        payload.expires_at,
                        payload.external_ref,
                        listing_id,
                    ),
                )
                listing = cursor.fetchone()
                cursor.execute(link_query, (payload.property_id, listing_id))
        return raise_if_not_found(listing, "Listing")
    except IntegrityError as exc:
        handle_error(exc, "Could not update listing")


#########################################
#               DELETE                  #
#########################################


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listing(listing_id: int, connection=Depends(get_db)):
    cleanup_queries = [
        "DELETE FROM listing_media WHERE listing_id = %s",
        "DELETE FROM open_houses WHERE listing_id = %s",
        "DELETE FROM saved_listings WHERE listing_id = %s",
        "DELETE FROM listing_agents WHERE listing_id = %s",
        "DELETE FROM listing_properties WHERE listing_id = %s",
    ]
    with connection:
        with connection.cursor() as cursor:
            for sql in cleanup_queries:
                cursor.execute(sql, (listing_id,))
            cursor.execute(
                "DELETE FROM listings WHERE id = %s RETURNING id", (listing_id,)
            )
            deleted = cursor.fetchone()
    raise_if_not_found(deleted, "Listing")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/listing-media/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_media(media_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection, "DELETE FROM listing_media WHERE id = %s RETURNING id", (media_id,)
    )
    raise_if_not_found(deleted, "Listing media")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/open-houses/{open_house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_open_house(open_house_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection,
        "DELETE FROM open_houses WHERE id = %s RETURNING id",
        (open_house_id,),
    )
    raise_if_not_found(deleted, "Open house")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


#########################################
#               PATCH                   #
#########################################


@router.patch("/{listing_id}/change/title")
def update_listing_title(
    listing_id: int,
    title: str,
    _: User = Depends(get_current_user),
    connection=Depends(get_db),
):
    listing_query = """
        UPDATE listings
        SET title = %s,
            updated_at = NOW()
        WHERE id = %s
        RETURNING *
    """
    patched = execute_returning(
        connection,
        listing_query,
        (
            title,
            listing_id,
        ),
    )

    return raise_if_not_found(patched, "Listings title")
