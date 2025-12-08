from typing import List, Optional
from db import fetch_all, execute_returning
from db_setup import run_setup
from fastapi import FastAPI, HTTPException, Depends, status, Response
from psycopg2 import IntegrityError
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    AddressCreate,
    LocationCreate,
    AddressUpdate,
    LocationUpdate,
    User,
    Token,
)
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from helpers import (
    get_db,
    raise_if_not_found,
    handle_error,
    get_current_user,
    authenticate_user,
    create_access_token,
)

from routers import all_routers


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

#########################################
#           SETUP ROUTERS               #
#########################################

for router in all_routers:
    app.include_router(router)


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
    parameters: List = []
    if city:
        query += " WHERE city ILIKE %s"
        parameters.append(f"%{city}%")

    query += " ORDER BY id"

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
        handle_error(exc, "Could not create address")


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
        handle_error(exc, "Could not create location")


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

        return raise_if_not_found(row, "Address")
    except IntegrityError as exc:
        handle_error(exc, "Could not update address")


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

        return raise_if_not_found(row, "Location")
    except IntegrityError as exc:
        handle_error(exc, "Could not update location")


#########################################
#               DELETE                  #
#########################################


@app.delete(
    "/listing-media/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["listings"],
)
def delete_media(media_id: int, connection=Depends(get_db)):
    deleted = execute_returning(
        connection, "DELETE FROM listing_media WHERE id = %s RETURNING id", (media_id,)
    )
    raise_if_not_found(deleted, "Listing media")
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
    raise_if_not_found(deleted, "Open house")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), connection=Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, connection)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires,
    )

    return {"access_token": access_token}


@app.get("/get/me", tags=["protected"])
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {"user_id": current_user.id, "username": current_user.username}
