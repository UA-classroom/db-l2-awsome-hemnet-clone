from typing import Optional
from datetime import datetime
from psycopg2.extensions import string_types
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


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_id: Optional[int] = None
    address_id: Optional[int] = None


class PropertyCreate(BaseModel):
    location_id: int
    property_type_id: int
    tenure_id: int
    year_built: Optional[int] = None
    living_area_sqm: Optional[float] = None
    additional_area_sqm: Optional[float] = None
    plot_area_sqm: Optional[float] = None
    rooms: Optional[float] = None
    floor: Optional[int] = None
    monthly_fee: Optional[float] = None
    energy_class: Optional[str] = None


class PropertyUpdate(PropertyCreate):
    pass


class ListingCreate(BaseModel):
    agent_id: int
    title: str
    description: Optional[str] = None
    status_id: int
    list_price: Optional[float] = None
    price_type_id: Optional[int] = None
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    external_ref: Optional[str] = None
    property_id: int


class ListingUpdate(BaseModel):
    agent_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    status_id: Optional[int] = None
    list_price: Optional[float] = None
    price_type_id: Optional[int] = None
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    external_ref: Optional[str] = None
    property_id: Optional[int] = None


class ListingMediaCreate(BaseModel):
    media_type_id: int
    url: str
    caption: Optional[str] = None
    position: Optional[int] = None


class OpenHouseCreate(BaseModel):
    starts_at: datetime
    ends_at: Optional[datetime] = None
    type_id: int
    note: Optional[str] = None


class SavedSearchCreate(BaseModel):
    query: str
    location: str
    price_min: float
    price_max: float
    rooms_min: float
    rooms_max: float
    property_types: list[str]
    send_email: bool = False


class AgencyCreate(BaseModel):
    name: str
    org_number: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    org_number: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None


class AgentCreate(BaseModel):
    user_id: int
    agency_id: Optional[int] = None
    title: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None


class AgentUpdate(BaseModel):
    user_id: Optional[int] = None
    agency_id: Optional[int] = None
    title: Optional[str] = None
    license_number: Optional[str] = None
    bio: Optional[str] = None


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    id: int
    username: str


class UserInDB(User):
    hashed_password: str
