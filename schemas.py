from typing import Optional

from pydantic import BaseModel


class AddressCreate(BaseModel):
    street_address: str
    postal_code: str
    city: str
    municipality: Optional[str] = None
    county: Optional[str] = None
    country: str


class AddressUpdate(AddressCreate):
    pass


class LocationCreate(BaseModel):
    street_address: str
    postal_code: str
    city: str
    municipality: Optional[str] = None
    county: Optional[str] = None
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationUpdate(LocationCreate):
    pass
