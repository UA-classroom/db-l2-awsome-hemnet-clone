from typing import Optional, List
from datetime import datetime
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


class LocationOut(BaseModel):
    id: int
    street_address: str
    postal_code: str
    city: str
    municipality: str
    county: str
    country: str
    latitude: float
    longitude: float


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    role_name: Optional[str] = None
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


class PropertyOut(BaseModel):
    id: int
    location_id: int
    property_type_id: int
    tenure_id: int
    year_built: int
    living_area_sqm: float
    additional_area_sqm: float
    plot_area_sqm: float
    rooms: float
    floor: int
    monthly_fee: float
    energy_class: str
    created_at: datetime
    updated_at: datetime


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
    title: Optional[str] = None
    description: Optional[str] = None
    status_id: Optional[int] = None
    list_price: Optional[float] = None
    price_type_id: Optional[int] = None
    published_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    external_ref: Optional[str] = None
    property_id: Optional[int] = None


class ListingItem(BaseModel):
    id: int
    title: str
    status: str
    list_price: float
    property_type: str
    rooms: float
    living_area_sqm: int
    city: str
    image: Optional[str] = None


class ListingOut(BaseModel):
    count: int
    items: List[ListingItem]


class ListingMediaCreate(BaseModel):
    media_type_id: int
    url: str
    caption: Optional[str] = None
    position: Optional[int] = None


class ListingDetailOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    list_price: float
    price_type_id: int
    published_at: datetime
    expires_at: datetime
    external_ref: str
    property_type: str
    tenure: str
    rooms: float
    living_area_sqm: float
    plot_area_sqm: Optional[float] = None
    energy_class: Optional[str] = None
    year_built: Optional[int] = None
    street_address: str
    postal_code: str
    city: str
    municipality: str
    agent_name: str
    agent_phone: str
    agency: str


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


class SavedSearchUpdate(BaseModel):
    query: Optional[str] = None
    location: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rooms_min: Optional[float] = None
    rooms_max: Optional[float] = None
    property_types: Optional[list[str]] = None
    send_email: Optional[bool] = None


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


class Item(BaseModel):
    title: str


class AutocompleteOut(BaseModel):
    count: int
    items: List[Item]


class ListingMediaItem(BaseModel):
    id: int
    media_type_id: int
    url: str
    caption: Optional[str]
    position: Optional[int]
    updated_at: datetime


class ListingMediaOut(BaseModel):
    count: int
    items: List[ListingMediaItem]


class OpenHouseItem(BaseModel):
    id: int
    starts_at: datetime
    ends_at: Optional[datetime]
    type: str
    note: Optional[str]


class OpenHousesItem(OpenHouseItem):
    listing_id: int


class OpenHousesOut(BaseModel):
    count: int
    items: List[OpenHousesItem]


class OpenHouseOut(BaseModel):
    count: int
    items: List[OpenHouseItem]


class UserMeOut(BaseModel):
    user_id: int
    username: str


class ListUser(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    role: Optional[str]


class UserOut(BaseModel):
    count: int
    items: List[ListUser]
