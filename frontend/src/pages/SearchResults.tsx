import { useMemo, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import type { FilterState } from '../components/FiltersSidebar'
import { FiltersSidebar } from '../components/FiltersSidebar'
import { PropertyCard } from '../components/PropertyCard'
import { SearchBar } from '../components/SearchBar'
import { useFavorites } from '../context/FavoritesContext'
import { mockProperties } from '../data/mockProperties'

const defaultFilters: FilterState = {
  location: '',
  price: [2000000, 9000000],
  minRooms: 0,
  propertyTypes: [],
}

export function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const { favorites, toggle } = useFavorites()
  const [filters, setFilters] = useState<FilterState>({
    ...defaultFilters,
    location: searchParams.get('location') ?? '',
  })

  const filtered = useMemo(() => {
    return mockProperties.filter((property) => {
      const matchLocation = filters.location
        ? property.address.toLowerCase().includes(filters.location.toLowerCase())
        : true
      const matchPrice = property.price >= filters.price[0] && property.price <= filters.price[1]
      const matchRooms = filters.minRooms === 0 || property.rooms >= filters.minRooms
      const matchType = filters.propertyTypes.length === 0 || filters.propertyTypes.includes(property.type)
      return matchLocation && matchPrice && matchRooms && matchType
    })
  }, [filters])

  const applySearch = (value: string) => {
    const params = new URLSearchParams(searchParams)
    params.set('location', value)
    setSearchParams(params)
    setFilters((prev) => ({ ...prev, location: value }))
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Search homes</h1>
          <p className="text-sm text-slate-600">Shareable filters via URL. Data wired for FastAPI backend.</p>
        </div>
        <SearchBar value={filters.location} onChange={applySearch} onSubmit={() => applySearch(filters.location)} />
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <FiltersSidebar filters={filters} onChange={setFilters} />
        <div className="space-y-4">
          <div className="flex items-center justify-between text-sm text-slate-600">
            <span>
              Showing {filtered.length} of {mockProperties.length} listings
            </span>
            <span className="rounded-full bg-emerald-50 px-3 py-1 font-semibold text-emerald-700">URL synced</span>
          </div>
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {filtered.map((property) => (
              <PropertyCard
                key={property.id}
                isFavorite={favorites.has(property.id)}
                onToggleFavorite={toggle}
                property={property}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
