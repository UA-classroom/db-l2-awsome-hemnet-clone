from typing import List, Optional
from db import fetch_all, fetch_one
from db_setup import get_connection, run_setup
from fastapi import FastAPI, HTTPException, Depends, status
from psycopg2 import OperationalError


tags_metadata = [
    {
        "name": "listings",
        "description": "Operations with listings.",
    },
]

app = FastAPI(title="Hemnet Clone API", version="1.0.0", openapi_tags=tags_metadata)

run_setup()


def get_db():
    con = get_connection()
    try:
        yield con
    except OperationalError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to Database",
        )
    finally:
        con.close()


def _raise_if_not_found(row, label: str):
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{label} not found"
        )
    return row


@app.get("/listings", tags=["listings"])
def list_listings(
    status_name: Optional[str] = None,
    city: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_rooms: Optional[float] = None,
    max_rooms: Optional[float] = None,
    conn=Depends(get_db),
):
    query = """
        SELECT l.id,
               l.title,
               ls.name AS status,
               l.list_price,
               pt.name AS property_type,
               p.rooms,
               p.living_area_sqm,
               loc.city
        FROM listings l
        JOIN listing_status ls ON l.status_id = ls.id
        JOIN listing_properties lp ON l.id = lp.listing_id
        JOIN properties p ON lp.property_id = p.id
        JOIN property_types pt ON p.property_type_id = pt.id
        JOIN locations loc ON p.location_id = loc.id
    """
    conditions: List[str] = []
    params: List = []

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

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY l.id"

    rows = fetch_all(conn, query, params)
    return {"count": len(rows), "items": rows}


@app.get("/listings/{listing_id}", tags=["listings"])
def listing_detail(listing_id: int, conn=Depends(get_db)):
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
    row = fetch_one(conn, query, (listing_id,))
    return _raise_if_not_found(row, "Listing")


@app.get("/listings/{listing_id}/media", tags=["listings"])
def listing_media(listing_id: int, conn=Depends(get_db)):
    query = """
        SELECT id, media_type_id, url, caption, position, updated_at
        FROM listing_media
        WHERE listing_id = %s
        ORDER BY position NULLS LAST, id
    """
    rows = fetch_all(conn, query, (listing_id,))
    return {"count": len(rows), "items": rows}


@app.get("/listings/{listing_id}/open-houses", tags=["listings"])
def listing_open_houses(listing_id: int, conn=Depends(get_db)):
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
    rows = fetch_all(conn, query, (listing_id,))
    return {"count": len(rows), "items": rows}
