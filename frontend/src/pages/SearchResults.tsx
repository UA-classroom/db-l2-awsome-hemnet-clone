import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { createSavedSearch, deleteSavedSearch, fetchProperties, fetchSavedSearches } from '../api/client'
import type { FilterState } from '../components/FiltersSidebar'
import { FiltersSidebar } from '../components/FiltersSidebar'
import { PropertyCard } from '../components/PropertyCard'
import { SearchBar } from '../components/SearchBar'
import { useAuth } from '../context/AuthContext'
import { useFavorites } from '../context/FavoritesContext'
import type { SavedSearch, SavedSearchFilters } from '../api/client'
import type { Property } from '../types'

const defaultFilters: FilterState = {
  free_text_search: '',
  location: '',
  price: [2000000, 9000000],
  minRooms: 0,
  maxRooms: Infinity,
  propertyTypes: [],
  status: 'for_sale',
}

const toSavedSearchFilters = (state: FilterState): SavedSearchFilters => {
  return {
    free_text_search: state.free_text_search || undefined,
    location: state.location || undefined,
    price: [state.price[0], state.price[1]],
    minRooms: state.minRooms,
    maxRooms: state.maxRooms === Infinity ? null : state.maxRooms,
    propertyTypes: state.propertyTypes.length ? [...state.propertyTypes] : [],
    status: state.status,
  }
}

const hydrateFiltersFromSavedSearch = (search: SavedSearch): FilterState => {
  const saved = search.filters
  const priceRange: [number, number] = saved?.price
    ? [saved.price[0], saved.price[1]]
    : [defaultFilters.price[0], defaultFilters.price[1]]

  return {
    ...defaultFilters,
    free_text_search: saved?.free_text_search ?? search.query ?? defaultFilters.free_text_search,
    location: saved?.location ?? defaultFilters.location,
    price: priceRange,
    minRooms: saved?.minRooms ?? defaultFilters.minRooms,
    maxRooms: saved?.maxRooms === null || saved?.maxRooms === undefined ? defaultFilters.maxRooms : saved.maxRooms,
    propertyTypes: saved?.propertyTypes ? [...saved.propertyTypes] : [...defaultFilters.propertyTypes],
    status: saved?.status ?? defaultFilters.status,
  }
}

export function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { favorites, toggle } = useFavorites()
  const { userId, isAuthenticated, isLoading: authLoading, token } = useAuth()
  const [results, setResults] = useState<Property[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [sendEmail, setSendEmail] = useState(true)
  const [filters, setFilters] = useState<FilterState>({
    ...defaultFilters,
    free_text_search: searchParams.get('free_text_search') ?? '',
    location: searchParams.get('location') ?? '',
  })

  const syncSearchParams = (next: FilterState) => {
    setSearchParams((prev) => {
      const params = new URLSearchParams(prev)
      if (next.free_text_search) params.set('free_text_search', next.free_text_search)
      else params.delete('free_text_search')
      if (next.location) params.set('location', next.location)
      else params.delete('location')
      return params
    })
  }

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetchProperties({
      free_text_search: filters.free_text_search,
      location: filters.location,
      minPrice: filters.price[0],
      maxPrice: filters.price[1],
      minRooms: filters.minRooms,
      maxRooms: filters.maxRooms,
      propertyTypes: filters.propertyTypes,
      status: filters.status,
    })
      .then((data) => {
        if (cancelled) return
        setResults(data)
      })
      .catch((err) => {
        console.error(err)
        if (cancelled) return
        setError('Could not load listings from API.')
        setResults([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [filters])

  useEffect(() => {
    if (!userId || !token) {
      setSavedSearches([])
      return
    }

    let cancelled = false
    fetchSavedSearches(userId, token, 20, 0).then((items) => {
      if (!cancelled) setSavedSearches(items)
    })

    return () => {
      cancelled = true
    }
  }, [token, userId])

  useEffect(() => {
    if (isAuthenticated) {
      setError(null)
    }
  }, [isAuthenticated])

  const addSavedSearch = async () => {
    if (!isAuthenticated) {
      setError('Log in to save this search.')
      return
    }
    if (!userId || !token) {
      setError('Loading your account... please try again in a moment.')
      return
    }
    setError(null)
    const query = filters.free_text_search || filters.location
    if (!query.trim()) {
      return
    }
    try {
      const filterPayload = toSavedSearchFilters(filters)
      const created = await createSavedSearch(userId, {
        query,
        location: filters.location /*|| filters.free_text_search || query*/,
        price_min: filters.price?.[0] ?? 0,
        price_max: filters.price?.[1] ?? 0,
        rooms_min: filters.minRooms ?? 0,
        rooms_max: Number.isFinite(filters.maxRooms) ? filters.maxRooms : 0,
        property_types: filters.propertyTypes.map((type) => type.toLowerCase()),
        send_email: sendEmail,
      }, token)
      const normalized = created.filters ? created : { ...created, filters: filterPayload }
      setSavedSearches((prev) => [normalized, ...prev])
    } catch (err) {
      console.error('Failed to save search', err)
      setError('Could not save this search.')
    }
  }

  const removeSavedSearch = async (id: string) => {
    if (!userId || !token) return
    try {
      await deleteSavedSearch(userId, id, token)
      setSavedSearches((prev) => prev.filter((item) => item.id !== id))
    } catch (err) {
      console.error('Failed to delete saved search', err)
      setError('Could not delete saved search.')
    }
  }

  const applyFreeTextSearch = (value: string) => {
    setFilters((prev) => {
      const next = { ...prev, free_text_search: value }
      syncSearchParams(next)
      return next
    })
  }

  const handleSavedSearchSelect = (search: SavedSearch) => {
    if (!search) return
    const restoredFilters = hydrateFiltersFromSavedSearch(search)
    setFilters(restoredFilters)
    syncSearchParams(restoredFilters)
  }

  const handleFiltersChange = (next: FilterState) => {
    setFilters(next)
    syncSearchParams(next)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Search homes</h1>
          <p className="text-sm text-slate-600">Shareable filters via URL. Data wired for FastAPI backend.</p>
        </div>
        <SearchBar value={filters.free_text_search} onChange={applyFreeTextSearch} onSubmit={applyFreeTextSearch} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <FiltersSidebar filters={filters} onChange={handleFiltersChange} />
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>
              {loading ? 'Loading listings…' : `Showing ${results.length} listings`}
            </span>
            <span className="rounded-full bg-emerald-50 px-3 py-1 font-semibold text-emerald-700">URL synced</span>
          </div>
          <div className="flex flex-col gap-3 rounded-2xl bg-white p-4 ring-1 ring-slate-100">
            <div className="flex flex-wrap items-center gap-3">
              <label className="flex items-center gap-2 text-xs text-slate-600">
                <input
                  checked={sendEmail}
                  className="accent-emerald-600"
                  type="checkbox"
                  onChange={(e) => setSendEmail(e.target.checked)}
                />
                Email alerts
              </label>
              <button
                className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500"
                disabled={authLoading || !isAuthenticated}
                type="button"
                onClick={addSavedSearch}
              >
                Save search
              </button>
            </div>
            {savedSearches.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {savedSearches.map((item) => (
                  <div
                    key={item.id}
                    className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700"
                  >
                    <button
                      className="text-left text-slate-700 transition hover:text-emerald-700"
                      type="button"
                      onClick={() => handleSavedSearchSelect(item)}
                    >
                      {item.query}
                    </button>
                    <button
                      aria-label="Delete saved search"
                      className="text-slate-400 transition hover:text-emerald-700"
                      type="button"
                      onClick={() => removeSavedSearch(item.id)}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {results.map((property) => (
              <PropertyCard
                key={property.id}
                isFavorite={favorites.has(property.id)}
                onToggleFavorite={toggle}
                property={property}
              />
            ))}
          </div>
          {!loading && !error && results.length === 0 && (
            <p className="text-sm text-slate-600">No listings match these filters.</p>
          )}
        </div>
      </div>
    </div>
  )
}
