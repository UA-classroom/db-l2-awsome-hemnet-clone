from typing import List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class AddressCreate(BaseModel):
    street_address: str
    postal_code: str
    city: str
    municipality: str | None = None
    county: str | None = None
    country: str


class AddressUpdate(AddressCreate):
    pass


class AddressOut(AddressCreate):
    id: int


class AddressIdOut(BaseModel):
    id: int


class LocationCreate(BaseModel):
    street_address: str
    postal_code: str
    city: str
    municipality: str | None = None
    county: str | None = None
    country: str
    latitude: float | None = None
    longitude: float | None = None


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
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role_name: str | None = None
    address_id: int | None = None


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=6)
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    role_name: str | None = None
    address_id: int | None = None


class UserCreateOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address_id: int | None = None
    created_at: datetime
    updated_at: datetime


class UserUpdateOut(BaseModel):
    id: int
    email: EmailStr
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    address_id: int | None = None
    created_at: datetime
    updated_at: datetime


class PropertyCreate(BaseModel):
    location_id: int
    property_type_id: int
    tenure_id: int
    year_built: int | None = None
    living_area_sqm: float | None = None
    additional_area_sqm: float | None = None
    plot_area_sqm: float | None = None
    rooms: float | None = None
    floor: int | None = None
    monthly_fee: float | None = None
    energy_class: str | None = None


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


class PropertyTypeItem(BaseModel):
    type: str


class ListingCreate(BaseModel):
    agent_id: int
    title: str
    description: str | None = None
    status_id: int
    list_price: float | None = None
    price_type_id: int | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    external_ref: str | None = None
    property_id: int


class ListingUpdate(BaseModel):
    agent_id: int | None = None
    title: str | None = None
    description: str | None = None
    status_id: int | None = None
    list_price: float | None = None
    price_type_id: int | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    external_ref: str | None = None
    property_id: int | None = None


class ListingItem(BaseModel):
    id: int
    title: str
    status: str
    list_price: float
    property_type: str
    rooms: float
    living_area_sqm: int
    city: str
    image: str | None = None


class ListingOut(BaseModel):
    count: int
    items: List[ListingItem]


class ListingMediaCreate(BaseModel):
    media_type_id: int
    url: str
    caption: str | None = None
    position: int | None = None


class ListingMutateOut(BaseModel):
    id: int
    agent_id: int
    title: str
    description: str | None = None
    status_id: int
    list_price: float | None = None
    price_type_id: int | None = None
    published_at: datetime | None = None
    expires_at: datetime | None = None
    external_ref: str | None = None
    created_at: datetime
    updated_at: datetime


class ListingDetailOut(BaseModel):
    id: int
    title: str
    description: str
    status: str
    list_price: float
    price_type_id: int
    published_at: datetime | None = None
    expires_at: datetime | None = None
    external_ref: str
    property_type: str
    tenure: str
    rooms: float
    living_area_sqm: float
    plot_area_sqm: float | None = None
    energy_class: str | None = None
    year_built: int | None = None
    street_address: str
    postal_code: str
    city: str
    municipality: str
    agent_name: str
    agent_phone: str
    agency: str


class OpenHouseCreate(BaseModel):
    starts_at: datetime
    ends_at: datetime | None = None
    type_id: int
    note: str | None = None


class OpenHouseCreateOut(BaseModel):
    id: int
    listing_id: int
    starts_at: datetime
    ends_at: datetime | None = None
    type_id: int
    note: str | None = None


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
    query: str | None = None
    location: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    rooms_min: float | None = None
    rooms_max: float | None = None
    property_types: list[str] | None = None
    send_email: bool | None = None


class AgencyCreate(BaseModel):
    name: str
    org_number: str | None = None
    phone: str | None = None
    website: str | None = None


class AgencyUpdate(BaseModel):
    name: str | None = None
    org_number: str | None = None
    phone: str | None = None
    website: str | None = None


class AgencyItem(BaseModel):
    id: int
    name: str
    org_number: str | None = None
    phone: str | None = None
    website: str | None = None


class AgenciesOut(BaseModel):
    count: int
    items: List[AgencyItem]


class AgencyDetailOut(AgencyItem):
    pass


class AgencyCreateOut(AgencyItem):
    created_at: datetime


class AgencyUpdateOut(AgencyItem):
    created_at: datetime
    updated_at: datetime


class AgentCreate(BaseModel):
    user_id: int
    agency_id: int | None = None
    title: str | None = None
    license_number: str | None = None
    bio: str | None = None


class AgentUpdate(BaseModel):
    user_id: int | None = None
    agency_id: int | None = None
    title: str | None = None
    license_number: str | None = None
    bio: str | None = None


class AgentListItem(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr
    phone: str | None = None
    title: str | None = None
    license_number: str | None = None
    agency: str | None = None


class AgentsOut(BaseModel):
    count: int
    items: List[AgentListItem]


class AgentDetailOut(AgentListItem):
    bio: str | None = None


class AgentCreateOut(BaseModel):
    id: int
    user_id: int
    title: str | None = None
    license_number: str | None = None
    bio: str | None = None
    created_at: datetime


class AgentUpdateOut(AgentCreateOut):
    updated_at: datetime


class AgentNameOut(BaseModel):
    title: str | None = None


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    username: str | None = None


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


class SavedListingItem(BaseModel):
    id: int
    created_at: datetime
    listing_id: int
    title: str
    list_price: float
    status: str
    city: str
    property_type: str


class SavedListingsOut(BaseModel):
    count: int
    items: List[SavedListingItem]


class SavedListingCreateOut(BaseModel):
    id: int
    user_id: int
    listing_id: int
    created_at: datetime


class SavedSearchItem(BaseModel):
    id: int
    user_id: int
    query: str
    location: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    rooms_min: float | None = None
    rooms_max: float | None = None
    send_email: bool
    created_at: datetime
    updated_at: datetime


class SavedSearchListItem(BaseModel):
    id: int
    query: str
    location: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    rooms_min: float | None = None
    rooms_max: float | None = None
    send_email: bool
    created_at: datetime
    updated_at: datetime
    property_types: List[str] = Field(default_factory=list)


class SavedSearchesOut(BaseModel):
    count: int
    items: List[SavedSearchListItem]


class ListingMediaItem(BaseModel):
    id: int
    media_type_id: int
    url: str
    caption: str
    position: int
    updated_at: datetime


class ListingMediaCreateOut(ListingMediaItem):
    listing_id: int


class ListingMediaOut(BaseModel):
    count: int
    items: List[ListingMediaItem]


class OpenHouseItem(BaseModel):
    id: int
    starts_at: datetime
    ends_at: datetime
    type: str
    note: str


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
    first_name: str
    last_name: str
    email: str
    role: str


class UserOut(BaseModel):
    count: int
    items: List[ListUser]
