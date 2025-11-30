from typing import Optional

from pydantic import BaseModel, EmailStr, Field


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


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    address_id: Optional[int] = None
