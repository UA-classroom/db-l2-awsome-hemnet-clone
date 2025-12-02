from typing import List, Optional
from db import fetch_all, fetch_one, execute_returning, execute_with_row_count
from db_setup import get_connection, run_setup
from fastapi import FastAPI, HTTPException, Depends, status, Response
from psycopg2 import OperationalError, IntegrityError
from psycopg2.extras import RealDictCursor
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    AddressCreate,
    LocationCreate,
    UserCreate,
    PropertyCreate,
    ListingCreate,
    ListingMediaCreate,
    OpenHouseCreate,
    SavedSearchCreate,
    AddressUpdate,
    LocationUpdate,
    UserUpdate,
    PropertyUpdate,
    ListingUpdate,
    AgencyCreate,
    AgencyUpdate,
    AgentCreate,
    AgentUpdate,
)


tags_metadata = [
    {
        "name": "listings",
        "description": "Operations with listings info.",
    },
    {
        "name": "properties",
        "description": "Operations with property info.",
    },
    {
        "name": "agents",
        "description": "Operations with agents info.",
    },
    {"name": "agencies", "description": "Operations with agencies info."},
    {
        "name": "users",
        "description": "Operations with users info.",
    },
]

app = FastAPI(title="Hemnet Clone API", version="1.0.0", openapi_tags=tags_metadata)

origins = ["http://localhost:5173", "http://127.0.0.1:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

run_setup()


def get_db():
    conection = get_connection()
    try:
        yield conection
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Database",
        )
    finally:
        conection.close()


def _raise_if_not_found(row, label: str):
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found"
        )
    return row


def _handle_error(exc: IntegrityError, fallback: str = "Invalid data"):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=fallback
    ) from exc


#########################################
#               GET                     #
#########################################


@app.get("/autocomplete")
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


@app.get("/listings", tags=["listings"])
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
    params: List = []

    if free_text_search:
        conditions.append("l.title ILIKE %s OR loc.city ILIKE %s")
        search_term = f"{free_text_search}%"
        params.append(search_term)
        params.append(search_term)
    if status_name:
        conditions.append("ls.name = %s")
        params.append(status_name)
    if city:
        conditions.append("loc.city ILIKE %s")
        params.append(f"%{city}%")
    if min_price is not None:
        conditions.append("l.list_price >= %s")
        params.append(min_price)
    if max_price is not None:
        conditions.append("l.list_price <= %s")
        params.append(max_price)
    if min_rooms is not None:
        conditions.append("p.rooms >= %s")
        params.append(min_rooms)
    if max_rooms is not None:
        conditions.append("p.rooms <= %s")
        params.append(max_rooms)
    if property_type is not None:
        types = [t.strip() for t in property_type.split(",")]
        placeholders = ", ".join(["%s"] * len(types))
        conditions.append(f"pt.name IN ({placeholders})")
        params.extend(types)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY l.id"

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/listings/{listing_id}", tags=["listings"])
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
    return _raise_if_not_found(row, "Listing")


@app.get("/listings/{listing_id}/media", tags=["listings"])
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

    params: List = [listing_id]

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/listings/{listing_id}/open-houses", tags=["listings"])
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

    params: List = [listing_id]

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/properties/{property_id}", tags=["properties"])
def property_detail(property_id: int, connection=Depends(get_db)):
    query = """
        SELECT p.id,
               p.location_id,
               p.property_type_id,
               p.tenure_id,
               p.year_built,
               p.living_area_sqm,
               p.additional_area_sqm,
               p.plot_area_sqm,
               p.rooms,
               p.floor,
               p.monthly_fee,
               p.energy_class,
               p.created_at,
               p.updated_at
        FROM properties p
        WHERE p.id = %s
    """

    row = fetch_one(connection, query, (property_id,))
    return _raise_if_not_found(row, "Property")


@app.get("/agents", tags=["agents"])
def list_agents(
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT a.id,
               u.first_name,
               u.last_name,
               u.email,
               u.phone,
               a.title,
               a.license_number,
               ag.name AS agency
        FROM agents a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN agent_agencies aa ON a.id = aa.agent_id
        LEFT JOIN agencies ag ON aa.agency_id = ag.id
        ORDER BY a.id
    """

    params: List = []

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/agents/{agent_id}", tags=["agents"])
def agent_detail(agent_id: int, connection=Depends(get_db)):
    query = """
        SELECT a.id,
               u.first_name,
               u.last_name,
               u.email,
               u.phone,
               a.title,
               a.license_number,
               a.bio,
               ag.name AS agency
        FROM agents a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN agent_agencies aa ON a.id = aa.agent_id
        LEFT JOIN agencies ag ON aa.agency_id = ag.id
        WHERE a.id = %s
    """
    row = fetch_one(connection, query, (agent_id,))
    return _raise_if_not_found(row, "Agent")


@app.get("/agencies", tags=["agencies"])
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

    params: List = []

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/agencies/{agency_id}", tags=["agencies"])
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
    return _raise_if_not_found(row, "Agencies")


@app.get("/users", tags=["users"])
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

    params: List = []

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/users/{user_id}/saved-listings", tags=["users"])
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

    params: List = [user_id]

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/users/{user_id}/searches", tags=["users"])
def user_saved_searches(
    user_id: int,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT id, name, send_email, created_at, updated_at
        FROM saved_searches
        WHERE user_id = %s
        ORDER BY created_at DESC
    """

    params: List = [user_id]

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


# TBD: Vet inte om denna endpoint är nödvändigt
@app.get("/locations", tags=["properties"])
def list_locations(
    city: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    connection=Depends(get_db),
):
    query = """
        SELECT id, street_address, postal_code, city, municipality, county, country, latitude, longitude
        FROM locations
    """
    params: List = []
    if city:
        query += " WHERE city ILIKE %s"
        params.append(f"%{city}%")

    query += " ORDER BY id"

    if limit is not None:
        query += " LIMIT %s"
        params.append(limit)
    if offset is not None:
        query += " OFFSET %s"
        params.append(offset)

    rows = fetch_all(connection, query, params)
    return {"count": len(rows), "items": rows}


#########################################
#                POST                   #
#########################################


@app.post("/addresses", status_code=status.HTTP_201_CREATED, tags=["users"])
def create_address(payload: AddressCreate, connection=Depends(get_db)):
    query = """
        INSERT INTO addresses (street_address, postal_code, city, municipality, county, country)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.street_address,
                payload.postal_code,
                payload.city,
                payload.municipality,
                payload.county,
                payload.country,
            ),
        )

        return row
    except IntegrityError as exc:
        _handle_error(exc, "Could not create address")


@app.post("/locations", status_code=status.HTTP_201_CREATED, tags=["properties"])
def create_location(payload: LocationCreate, connection=Depends(get_db)):
    query = """
        INSERT INTO locations (street_address, postal_code, city, municipality, county, country, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.street_address,
                payload.postal_code,
                payload.city,
                payload.municipality,
                payload.county,
                payload.country,
                payload.latitude,
                payload.longitude,
            ),
        )

        return row
    except IntegrityError as exc:
        _handle_error(exc, "Could not create location")


@app.post("/users", status_code=status.HTTP_201_CREATED, tags=["users"])
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
        _handle_error(exc, "User could not be created (email might already exist)")


@app.post("/properties", status_code=status.HTTP_201_CREATED, tags=["properties"])
def create_property(payload: PropertyCreate, connection=Depends(get_db)):
    query = """
        INSERT INTO properties (
            location_id, property_type_id, tenure_id, year_built, living_area_sqm,
            additional_area_sqm, plot_area_sqm, rooms, floor, monthly_fee, energy_class
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.location_id,
                payload.property_type_id,
                payload.tenure_id,
                payload.year_built,
                payload.living_area_sqm,
                payload.additional_area_sqm,
                payload.plot_area_sqm,
                payload.rooms,
                payload.floor,
                payload.monthly_fee,
                payload.energy_class,
            ),
        )

        return row
    except IntegrityError as exc:
        _handle_error(exc, "Could not create property (check foreign keys)")


@app.post(
    "/listings",
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
        _handle_error(
            exc,
            "Could not create listing (check agent, status, or property references)",
        )


@app.post(
    "/listings/{listing_id}/media",
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
        _handle_error(exc, "Could not add listing media")


@app.post(
    "/listings/{listing_id}/open-houses",
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
        _handle_error(exc, "Could not create open house entry")


@app.post(
    "/users/{user_id}/saved-listings",
    status_code=status.HTTP_201_CREATED,
    tags=["users"],
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
        _handle_error(exc, "Listing already saved or invalid reference")


@app.post(
    "/users/{user_id}/searches", status_code=status.HTTP_201_CREATED, tags=["users"]
)
def create_saved_search(
    user_id: int, payload: SavedSearchCreate, connection=Depends(get_db)
):
    query = """
        INSERT INTO saved_searches (user_id, name, send_email)
        VALUES (%s, %s, %s)
        RETURNING id, user_id, name, send_email, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection, query, (user_id, payload.name, payload.send_email)
        )

        return row
    except IntegrityError as exc:
        _handle_error(exc, "Could not create saved search")


@app.post("/agents/{agency_id}", status_code=status.HTTP_201_CREATED, tags=["agents"])
def create_agent(payload: AgentCreate, connection=Depends(get_db)):
    query = """
        INSERT INTO agents (user_id, title, license_number, bio, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING id, user_id, title, license_number, bio, created_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (payload.user_id, payload.title, payload.license_number, payload.bio),
        )

        if row is not None and payload.agency_id is not None:
            execute_with_row_count(
                connection,
                """agent_id: int,
                    INSERT INTO agent_agencies (agency_id, agent_id)
                    VALUES (%s, %s)
                """,
                (
                    payload.agency_id,
                    row["id"],
                ),
            )

        return row
    except IntegrityError as exc:
        _handle_error(exc, "Could not create agent")


@app.post("/agencies", status_code=status.HTTP_201_CREATED, tags=["agencies"])
def create_agency(payload: AgencyCreate, connection=Depends(get_db)):
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
        _handle_error(exc, "Could not create saved search")


#########################################
#               PUT                     #
#########################################


@app.put("/addresses/{address_id}", tags=["users"])
def update_address(address_id: int, payload: AddressUpdate, connection=Depends(get_db)):
    query = """
        UPDATE addresses
        SET street_address = %s,
            postal_code = %s,
            city = %s,
            municipality = COALESCE(%s, municipality),
            county = COALESCE(%s, county),
            country = %s
        WHERE id = %s
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.street_address,
                payload.postal_code,
                payload.city,
                payload.municipality,
                payload.county,
                payload.country,
                address_id,
            ),
        )

        return _raise_if_not_found(row, "Address")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update address")


@app.put("/locations/{location_id}", tags=["properties"])
def update_location(
    location_id: int, payload: LocationUpdate, connection=Depends(get_db)
):
    query = """
        UPDATE locations
        SET street_address = %s,
            postal_code = %s,
            city = %s,
            municipality = COALESCE(%s, municipality),
            county = COALESCE(%s, county),
            country = %s,
            latitude = COALESCE(%s, latitude),
            longitude = COALESCE(%s, longitude)
        WHERE id = %s
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.street_address,
                payload.postal_code,
                payload.city,
                payload.municipality,
                payload.county,
                payload.country,
                payload.latitude,
                payload.longitude,
                location_id,
            ),
        )

        return _raise_if_not_found(row, "Location")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update location")


@app.put("/users/{user_id}", tags=["users"])
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

        return _raise_if_not_found(row, "User")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update user")


@app.put("/properties/{property_id}", tags=["properties"])
def update_property(
    property_id: int, payload: PropertyUpdate, connection=Depends(get_db)
):
    query = """
        UPDATE properties
        SET location_id = %s,
            property_type_id = %s,
            tenure_id = %s,
            year_built = COALESCE(%s, year_built)
            living_area_sqm = COALESCE(%s, living_area_sqm)
            additional_area_sqm = COALESCE(%s, additional_area_sqm)
            plot_area_sqm = COALESCE(%s, plot_area_sqm)
            rooms = COALESCE(%s, rooms)
            floor = COALESCE(%s, floor)
            monthly_fee = COALESCE(%s, monthly_fee)
            energy_class = COALESCE(%s, energy_class)
            updated_at = NOW()
        WHERE id = %s
        RETURNING *
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.location_id,
                payload.property_type_id,
                payload.tenure_id,
                payload.year_built,
                payload.living_area_sqm,
                payload.additional_area_sqm,
                payload.plot_area_sqm,
                payload.rooms,
                payload.floor,
                payload.monthly_fee,
                payload.energy_class,
                property_id,
            ),
        )

        return _raise_if_not_found(row, "Property")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update property")


@app.put("/listings/{listing_id}", tags=["listings"])
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
        return _raise_if_not_found(listing, "Listing")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update listing")


@app.put("/users/{user_id}/searches/{search_id}", tags=["users"])
def update_saved_search(
    user_id: int,
    search_id: int,
    name: str,
    send_email: bool = False,
    connection=Depends(get_db),
):
    query = """
        UPDATE saved_searches
        SET name = %s,
            send_email = %s,
            updated_at = NOW()
        WHERE id = %s AND user_id = %s
        RETURNING id, user_id, name, send_email, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection, query, (name, send_email, search_id, user_id)
        )
        return _raise_if_not_found(row, "Saved search")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update saved search")


@app.put("/agents/{agent_id}", tags=["agents"])
def update_agent(agent_id: int, payload: AgentUpdate, connection=Depends(get_db)):
    query = """
        UPDATE agents
        SET user_id = COALESCE(%s, user_id),
            title = COALESCE(%s, title),
            license_number = COALESCE(%s, license_number),
            bio = COALESCE(%s, bio),
            updated_at = NOW()
        WHERE id = %s
        RETURNING id, user_id, title, license_number, bio, created_at, updated_at
    """
    try:
        row = execute_returning(
            connection,
            query,
            (
                payload.user_id,
                payload.title,
                payload.license_number,
                payload.bio,
                agent_id,
            ),
        )

        if row is not None and payload.agency_id is not None:
            execute_with_row_count(
                connection,
                """
                    UPDATE agent_agencies 
                    SET agency_id = %s 
                    WHERE agent_id = %s 
                """,
                (
                    payload.agency_id,
                    agent_id,
                ),
            )

        return _raise_if_not_found(row, "Saved search")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update agent")


@app.put("/agenies/{agency_id}", tags=["agencies"])
def update_agency(agency_id: int, payload: AgencyUpdate, connection=Depends(get_db)):
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

        return _raise_if_not_found(row, "Saved search")
    except IntegrityError as exc:
        _handle_error(exc, "Could not update agency")


#########################################
#               DELETE                  #
#########################################


@app.delete(
    "/listings/{listing_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["listings"]
)
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
    _raise_if_not_found(deleted, "Listing")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["properties"],
)
def delete_property(property_id: int, connection=Depends(get_db)):
    in_use = fetch_one(
        connection,
        "SELECT COUNT(*) AS count FROM listing_properties WHERE property_id = %s",
        (property_id,),
    )
    if in_use and in_use["count"] > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Property is linked to listings. Remove links before deleting.",
        )
    deleted = execute_returning(
        connection, "DELETE FROM properties WHERE id = %s RETURNING id", (property_id,)
    )
    _raise_if_not_found(deleted, "Property")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/listing-media/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["listings"],
)
def delete_media(media_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection, "DELETE FROM listing_media WHERE id = %s RETURNING id", (media_id,)
    )
    _raise_if_not_found(deleted, "Listing media")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/open-houses/{open_house_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["listings"],
)
def delete_open_house(open_house_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection,
        "DELETE FROM open_houses WHERE id = %s RETURNING id",
        (open_house_id,),
    )
    _raise_if_not_found(deleted, "Open house")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
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
    _raise_if_not_found(deleted, "Saved listing")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
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
    _raise_if_not_found(deleted, "Saved search")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/agents/{agent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["agents"],
)
def delete_agent(agent_id: int, connection=Depends(get_db)):
    execute_returning(
        connection, "DELETE FROM agent_agencies WHERE agent_id = %s", (agent_id,)
    )

    deleted = execute_returning(
        connection,
        "DELETE FROM agents WHERE id = %s RETURNING id",
        (agent_id,),
    )
    _raise_if_not_found(deleted, "Saved search")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.delete(
    "/agencies/{agency_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["agencies"],
)
def delete_agency(agency_id: int, connection=Depends(get_db)):
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
    _raise_if_not_found(deleted, "Saved search")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
