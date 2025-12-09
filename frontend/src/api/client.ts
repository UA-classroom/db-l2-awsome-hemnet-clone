import type { OpenHouse, Property } from '../types'

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
  free_text_search?: string
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

export type SavedSearchFilters = {
  free_text_search?: string
  location?: string
  price?: [number, number]
  minRooms?: number
  maxRooms?: number | null
  propertyTypes?: string[]
  status?: string
}

export type SavedSearch = {
  id: string
  query: string
  send_email: boolean
  filters?: SavedSearchFilters | null
  created_at?: string
  updated_at?: string
}

type ApiSavedSearch = Omit<SavedSearch, 'id' | 'filters'> & {
  id: string | number
  filters?: SavedSearchFilters | string | null
  location?: string | null
  price_min?: number | null
  price_max?: number | null
  rooms_min?: number | null
  rooms_max?: number | null
  property_types?: string[] | null
  status_name?: string | null
}

type AutocompleteResponse = {
  items?: { title?: string }[]
  count?: number
}

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers)
  headers.set('Content-Type', 'application/json')

  const res = await fetch(`${BASE_URL}${path}`, {
    ...init,
    headers,
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

function parseSavedSearchFilters(filters?: SavedSearchFilters | string | null): SavedSearchFilters | undefined {
  if (!filters) {
    return undefined
  }

  let raw: Record<string, unknown> | SavedSearchFilters

  if (typeof filters === 'string') {
    try {
      raw = JSON.parse(filters) as Record<string, unknown>
    } catch (error) {
      console.warn('Failed to parse saved search filters', error)
      return undefined
    }
  } else {
    raw = filters
  }

  const propertyTypes =
    (Array.isArray((raw as any).propertyTypes) && (raw as any).propertyTypes) ||
    (Array.isArray((raw as any).property_types) && (raw as any).property_types)

  const priceMin = (raw as any).price_min
  const priceMax = (raw as any).price_max
  const roomsMin = (raw as any).rooms_min
  const roomsMax = (raw as any).rooms_max
  const status = (raw as any).status ?? (raw as any).status_name

  const normalized: SavedSearchFilters = {
    free_text_search: (raw as any).free_text_search ?? (raw as any).query,
    location: (raw as any).location ?? (raw as any).city,
    price:
      Array.isArray((raw as any).price) && (raw as any).price.length === 2
        ? ((raw as any).price as [number, number])
        : typeof priceMin === 'number' && typeof priceMax === 'number'
          ? [priceMin, priceMax]
          : undefined,
    minRooms: (raw as any).minRooms ?? (typeof roomsMin === 'number' ? roomsMin : undefined),
    maxRooms:
      (raw as any).maxRooms ??
      (typeof roomsMax === 'number' || roomsMax === null ? (roomsMax as number | null) : undefined),
    propertyTypes: propertyTypes ? propertyTypes.map((type: unknown) => String(type).toLowerCase()) : undefined,
    status: typeof status === 'string' ? status : undefined,
  }

  return normalized
}

function deriveFiltersFromFlatFields(item: ApiSavedSearch): SavedSearchFilters | undefined {
  const hasPriceRange = typeof item.price_min === 'number' && typeof item.price_max === 'number'
  const hasMinRooms = typeof item.rooms_min === 'number'
  const hasMaxRooms = typeof item.rooms_max === 'number' || item.rooms_max === null
  const hasPropertyTypes = Array.isArray(item.property_types) && item.property_types.length > 0
  const hasLocation = typeof item.location === 'string' && item.location.trim().length > 0
  const hasStatus = typeof item.status_name === 'string' && item.status_name.trim().length > 0
  const hasQuery = typeof item.query === 'string' && item.query.trim().length > 0

  if (!(hasPriceRange || hasMinRooms || hasMaxRooms || hasPropertyTypes || hasLocation || hasStatus || hasQuery)) {
    return undefined
  }

  const propertyTypes = hasPropertyTypes ? item.property_types?.filter(Boolean).map((type) => type.toLowerCase()) : undefined

  return {
    free_text_search: hasQuery ? item.query : undefined,
    location: hasLocation ? item.location ?? undefined : undefined,
    price: hasPriceRange ? [item.price_min as number, item.price_max as number] : undefined,
    minRooms: hasMinRooms ? item.rooms_min ?? undefined : undefined,
    maxRooms: hasMaxRooms ? (item.rooms_max === null ? null : (item.rooms_max as number)) : undefined,
    propertyTypes,
    status: hasStatus ? item.status_name ?? undefined : undefined,
  }
}

function normalizeSavedSearch(item: ApiSavedSearch): SavedSearch {
  const parsedFilters = parseSavedSearchFilters(item.filters)
  const derivedFilters = parsedFilters ?? deriveFiltersFromFlatFields(item)

  return {
    id: String(item.id),
    query: item.query,
    send_email: item.send_email,
    filters: derivedFilters,
    created_at: item.created_at,
    updated_at: item.updated_at,
  }
}

export async function fetchProperties(filters: PropertyFilters = {}): Promise<Property[]> {
  const params = new URLSearchParams()
  if (filters.free_text_search) params.append('free_text_search', filters.free_text_search)
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

export async function fetchAutocomplete(searchTerm: string, signal?: AbortSignal): Promise<string[]> {
  const trimmed = searchTerm.trim()
  if (!trimmed) {
    return []
  }

  const params = new URLSearchParams({ search_term: trimmed })

  try {
    const data = await fetchJson<AutocompleteResponse>(`/listings/autocomplete?${params.toString()}`, { signal })
    return (data.items ?? []).map((item) => item.title).filter((title): title is string => Boolean(title))
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      throw error
    }
    console.error('Failed to fetch autocomplete suggestions', error)
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

export async function fetchSavedListings(userId: number, token: string): Promise<string[]> {
  if (!token) {
    throw new Error('Missing auth token for fetching saved listings')
  }

  try {
    const data = await fetchJson<{ items?: { listing_id: number | string }[] }>(`/users/${userId}/saved-listings`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return (data.items ?? []).map((item) => String(item.listing_id))
  } catch (error) {
    console.error('Failed to fetch saved listings', error)
    return []
  }
}

export async function saveFavoriteListing(userId: number, listingId: string, token: string): Promise<void> {
  if (!token) {
    throw new Error('Missing auth token for saving favorite')
  }

  const res = await fetch(`${BASE_URL}/users/${userId}/saved-listings?listing_id=${listingId}`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to save favorite (${res.status})`)
  }
}

export async function deleteFavoriteListing(userId: number, listingId: string, token: string): Promise<void> {
  if (!token) {
    throw new Error('Missing auth token for deleting favorite')
  }

  const res = await fetch(`${BASE_URL}/users/${userId}/saved-listings/${listingId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to delete favorite (${res.status})`)
  }
}

export async function fetchSavedSearches(
  userId: number,
  token: string,
  limit?: number,
  offset?: number,
): Promise<SavedSearch[]> {
  if (!token) {
    throw new Error('Missing auth token for fetching saved searches')
  }

  const params = new URLSearchParams()
  if (limit !== undefined) params.append('limit', String(limit))
  if (offset !== undefined) params.append('offset', String(offset))

  try {
    const data = await fetchJson<{ items?: ApiSavedSearch[] }>(`/users/${userId}/searches?${params.toString()}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })
    return data.items?.map(normalizeSavedSearch) ?? []
  } catch (error) {
    console.error('Failed to fetch saved searches', error)
    return []
  }
}

export type CreateSavedSearchPayload = {
  query: string
  location: string
  price_min: number
  price_max: number
  rooms_min: number
  rooms_max: number
  property_types: string[]
  send_email: boolean
}

export async function createSavedSearch(userId: number, payload: CreateSavedSearchPayload, token: string) {
  if (!token) {
    throw new Error('Missing auth token for creating saved search')
  }

  const res = await fetch(`${BASE_URL}/users/${userId}/searches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Failed to create saved search (${res.status})`)
  }

  const data = (await res.json()) as ApiSavedSearch
  return normalizeSavedSearch(data)
}

export async function deleteSavedSearch(userId: number, searchId: string, token: string) {
  if (!token) {
    throw new Error('Missing auth token for deleting saved search')
  }

  const res = await fetch(`${BASE_URL}/users/${userId}/searches/${searchId}`, {
    method: 'DELETE',
    headers: {
      Authorization: `Bearer ${token}`,
    },
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
    const data = await fetchJson<{ items?: { id: number; starts_at: string; ends_at: string; type: string; note?: string | null }[] }>(
      `/listings/${id}/open/houses`,
    )
    return (
      data.items?.map(
        (item): OpenHouse => ({
          id: String(item.id),
          startsAt: item.starts_at,
          endsAt: item.ends_at,
          type: item.type,
          note: item.note,
        }),
      ) ?? []
    )
  } catch (error) {
    console.error(`Failed to fetch open houses for listing ${id}`, error)
    return []
  }
}

export async function fetchLatestOpenHouses(limit?: number, offset?: number) {
  const params = new URLSearchParams()
  if (limit !== undefined) params.append('limit', String(limit))
  if (offset !== undefined) params.append('offset', String(offset))
  const query = params.toString()
  const path = query ? `/listings/open/houses?${query}` : '/listings/open/houses'

  try {
    const data = await fetchJson<{
      items?: { id: number; listing_id?: number | string; starts_at: string; ends_at: string; type: string; note?: string | null }[]
    }>(path)
    return (
      data.items?.map(
        (item): OpenHouse => ({
          id: String(item.id),
          listingId: item.listing_id ? String(item.listing_id) : undefined,
          startsAt: item.starts_at,
          endsAt: item.ends_at,
          type: item.type,
          note: item.note,
        }),
      ) ?? []
    )
  } catch (error) {
    console.error('Failed to fetch latest open houses', error)
    return []
  }
}

export { BASE_URL }
