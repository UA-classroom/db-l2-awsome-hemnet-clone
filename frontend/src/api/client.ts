import type { Property } from '../types'

const BASE_URL = 'http://127.0.0.1:8000'
const PLACEHOLDER_IMAGE = 'https://images.unsplash.com/photo-1505691723518-36a5ac3be353?auto=format&fit=crop&w=1200&q=80'

type ApiProperty = {
  id: string | number
  title?: string
  description?: string
  status?: string
  list_price?: number
  price_type_id?: number
  property_type?: string
  type?: string
  tenure?: string
  rooms?: number
  living_area_sqm?: number
  plot_area_sqm?: number | null
  street_address?: string
  address?: string
  postal_code?: string
  city?: string
  municipality?: string
  image?: string
  images?: string[]
  agent_name?: string
  agent_phone?: string
  agency?: string
}

export type PropertyFilters = {
  location?: string
  minPrice?: number
  maxPrice?: number
  minRooms?: number
  maxRooms?: number
  propertyTypes?: string[]
  status?: string
  limit?: number
  offset?: number
}

export type SavedSearch = {
  id: string
  name: string
  send_email: boolean
  created_at?: string
  updated_at?: string
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  })

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }

  return res.json() as Promise<T>
}

function normalizeProperty(raw: ApiProperty): Property {
  const images = raw.images && raw.images.length > 0 ? raw.images : raw.image ? [raw.image] : [PLACEHOLDER_IMAGE]
  const price = raw.list_price ?? 0
  const area = raw.living_area_sqm ?? 0
  const type = raw.type ?? raw.property_type ?? 'Unknown'
  const address = raw.street_address ?? raw.address ?? raw.city ?? 'Address unavailable'

  return {
    id: String(raw.id),
    title: raw.title ?? 'Untitled home',
    address,
    price,
    rooms: raw.rooms ?? 0,
    area,
    type,
    image: images[0],
    images,
    description: raw.description ?? 'No description available.',
    broker: { name: raw.agent_name ?? 'Broker pending', phone: raw.agent_phone ?? '' },
    tags: [],
    isFavorite: false,
    status: raw.status,
  }
}

export async function fetchProperties(filters: PropertyFilters = {}): Promise<Property[]> {
  const params = new URLSearchParams()
  if (filters.location) params.append('city', filters.location)
  if (filters.minPrice !== undefined) params.append('min_price', String(filters.minPrice))
  if (filters.maxPrice !== undefined) params.append('max_price', String(filters.maxPrice))
  if (filters.minRooms !== undefined && filters.minRooms > 0) params.append('min_rooms', String(filters.minRooms))
  if (filters.maxRooms !== undefined && filters.maxRooms !== Infinity && filters.maxRooms > 0)
    params.append('max_rooms', String(filters.maxRooms))
  if (filters.propertyTypes && filters.propertyTypes.length > 0)
    params.append('property_type', filters.propertyTypes.join(','))
  if (filters.status) params.append('status_name', filters.status)
  if (filters.limit) params.append('limit', String(filters.limit))
  if (filters.offset) params.append('offset', String(filters.offset))

  try {
    const data = await fetchJson<{ items?: ApiProperty[]; count?: number } | ApiProperty[]>(`/listings?${params.toString()}`)
    const items = Array.isArray(data) ? data : data?.items ?? []
    return items.map(normalizeProperty)
  } catch (error) {
    console.error('Failed to fetch properties', error)
    return []
  }
}

export async function fetchProperty(id: string): Promise<Property | null> {
  try {
    const data = await fetchJson<ApiProperty>(`/listings/${id}`)
    return normalizeProperty(data)
  } catch (error) {
    console.error(`Failed to fetch property ${id}`, error)
    return null
  }
}

export async function fetchSavedListings(userId: string): Promise<string[]> {
  try {
    const data = await fetchJson<{ items?: { listing_id: number | string }[] }>(`/users/${userId}/saved-listings`)
    return (data.items ?? []).map((item) => String(item.listing_id))
  } catch (error) {
    console.error('Failed to fetch saved listings', error)
    return []
  }
}

export async function saveFavoriteListing(userId: string, listingId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/users/${userId}/saved-listings?listing_id=${listingId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to save favorite (${res.status})`)
  }
}

export async function deleteFavoriteListing(userId: string, listingId: string): Promise<void> {
  const res = await fetch(`${BASE_URL}/users/${userId}/saved-listings/${listingId}`, {
    method: 'DELETE',
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to delete favorite (${res.status})`)
  }
}

export async function fetchSavedSearches(userId: string, limit?: number, offset?: number): Promise<SavedSearch[]> {
  const params = new URLSearchParams()
  if (limit !== undefined) params.append('limit', String(limit))
  if (offset !== undefined) params.append('offset', String(offset))

  try {
    const data = await fetchJson<{ items?: SavedSearch[] }>(`/users/${userId}/searches?${params.toString()}`)
    return data.items?.map((item) => ({ ...item, id: String(item.id) })) ?? []
  } catch (error) {
    console.error('Failed to fetch saved searches', error)
    return []
  }
}

export async function createSavedSearch(userId: string, payload: { name: string; send_email: boolean }) {
  const res = await fetch(`${BASE_URL}/users/${userId}/searches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to create saved search (${res.status})`)
  }

  return res.json() as Promise<SavedSearch>
}

export async function deleteSavedSearch(userId: string, searchId: string) {
  const res = await fetch(`${BASE_URL}/users/${userId}/searches/${searchId}`, {
    method: 'DELETE',
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to delete saved search (${res.status})`)
  }
}

export async function fetchListingMedia(id: string): Promise<string[]> {
  try {
    const data = await fetchJson<{ items?: { url: string; position?: number }[]; count?: number }>(`/listings/${id}/media`)
    const items = data.items ?? []
    return items
      .sort((a, b) => (a.position ?? 0) - (b.position ?? 0))
      .map((item) => item.url)
      .filter(Boolean)
  } catch (error) {
    console.error(`Failed to fetch media for listing ${id}`, error)
    return []
  }
}

export async function fetchListingOpenHouses(id: string) {
  try {
    const data = await fetchJson<{ items?: { starts_at: string; ends_at: string; type: string; note?: string | null }[] }>(
      `/listings/${id}/open-houses`,
    )
    return data.items ?? []
  } catch (error) {
    console.error(`Failed to fetch open houses for listing ${id}`, error)
    return []
  }
}

export { BASE_URL }
