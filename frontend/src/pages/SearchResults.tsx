import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { createSavedSearch, deleteSavedSearch, fetchProperties, fetchSavedSearches } from '../api/client'
import type { FilterState } from '../components/FiltersSidebar'
import { FiltersSidebar } from '../components/FiltersSidebar'
import { PropertyCard } from '../components/PropertyCard'
import { SearchBar } from '../components/SearchBar'
import { useFavorites } from '../context/FavoritesContext'
import type { Property } from '../types'
import type { SavedSearch } from '../api/client'

const defaultFilters: FilterState = {
  free_text_search: '',
  location: '',
  price: [2000000, 9000000],
  minRooms: 0,
  maxRooms: Infinity,
  propertyTypes: [],
  status: 'for_sale',
}

export function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { favorites, toggle } = useFavorites()
  const [results, setResults] = useState<Property[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([])
  const [sendEmail, setSendEmail] = useState(true)
  const [filters, setFilters] = useState<FilterState>({
    ...defaultFilters,
    location: searchParams.get('location') ?? '',
  })
  const userId = '1' // TODO: replace with auth user

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
    let cancelled = false
    fetchSavedSearches(userId, 20, 0).then((items) => {
      if (!cancelled) setSavedSearches(items)
    })
    return () => {
      cancelled = true
    }
  }, [userId])

  const addSavedSearch = async () => {
    if (filters.location === null) {
      return;
    }
    const name = filters.location
    try {
      const created = await createSavedSearch(userId, { name, send_email: sendEmail })
      setSavedSearches((prev) => [{ ...created, id: String(created.id) }, ...prev])
    } catch (err) {
      console.error('Failed to save search', err)
      setError('Could not save this search.')
    }
  }

  const removeSavedSearch = async (id: string) => {
    try {
      await deleteSavedSearch(userId, id)
      setSavedSearches((prev) => prev.filter((item) => item.id !== id))
    } catch (err) {
      console.error('Failed to delete saved search', err)
      setError('Could not delete saved search.')
    }
  }

  const applySearch = (value: string) => {
    const params = new URLSearchParams(searchParams)
    params.set('location', value)
    setSearchParams(params)
    setFilters((prev) => ({ ...prev, location: value }))
  }

  const handleSavedSearchSelect = (searchName: string) => {
    if (!searchName) return
    applySearch(searchName)
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Search homes</h1>
          <p className="text-sm text-slate-600">Shareable filters via URL. Data wired for FastAPI backend.</p>
        </div>
        <SearchBar value={filters.location} onChange={applySearch} onSubmit={applySearch} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <FiltersSidebar filters={filters} onChange={setFilters} />
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
                className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
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
                      onClick={() => handleSavedSearchSelect(item.name)}
                    >
                      {item.name}
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
