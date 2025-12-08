from fastapi import APIRouter, Depends, status, Response, HTTPException
from psycopg2 import IntegrityError
from db import fetch_one, execute_returning
from helpers import (
    get_db,
    raise_if_not_found,
    handle_error,
)
from schemas import (
    PropertyCreate,
    PropertyUpdate,
)


router = APIRouter(
    prefix="/properties",
    tags=["properties"],
)

#########################################
#               GET                     #
#########################################


@router.get("/{property_id}")
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
    return raise_if_not_found(row, "Property")


#########################################
#                POST                   #
#########################################


@router.post("/", status_code=status.HTTP_201_CREATED)
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
        handle_error(exc, "Could not create property (check foreign keys)")


#########################################
#               PUT                     #
#########################################


@router.put("/{property_id}")
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

        return raise_if_not_found(row, "Property")
    except IntegrityError as exc:
        handle_error(exc, "Could not update property")


#########################################
#               DELETE                  #
#########################################


@router.delete(
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
    raise_if_not_found(deleted, "Property")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
