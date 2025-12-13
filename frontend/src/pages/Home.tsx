import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { fetchLatestOpenHouses, fetchProperties } from '../api/client'
import { PropertyCard } from '../components/PropertyCard'
import { SearchBar } from '../components/SearchBar'
import { useFavorites } from '../context/FavoritesContext'
import type { OpenHouse, Property } from '../types'

export function HomePage() {
  const navigate = useNavigate()
  const { favorites, toggle } = useFavorites()
  const [search, setSearch] = useState('')
  const [featured, setFeatured] = useState<Property[]>([])
  const [openHouses, setOpenHouses] = useState<OpenHouse[]>([])

  useEffect(() => {
    fetchProperties({ limit: 6, status: 'for_sale' }).then((data) => setFeatured(data.slice(0, 3)))
    fetchLatestOpenHouses(3, 0).then((items) => setOpenHouses(items))
  }, [])

  const goToSearch = (nextSearch: string) => navigate(`/search?free_text_search=${encodeURIComponent(nextSearch)}`)

  return (
    <div className="space-y-10 lg:space-y-14">
      <section className="relative overflow-hidden rounded-3xl bg-white p-8 shadow-lg ring-1 ring-slate-100 lg:p-12">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_10%_20%,rgba(16,185,129,0.08),transparent_25%),radial-gradient(circle_at_90%_10%,rgba(16,185,129,0.06),transparent_20%)]" />
        <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
          <div className="space-y-6">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Hemnet Clone</p>
            <h1 className="text-4xl font-bold text-slate-900 lg:text-5xl">
              Find bright Scandinavian homes with confidence.
            </h1>
            <p className="text-lg text-slate-600">
              Search curated listings, track favorites, and explore details powered by the homeless.
            </p>
            <SearchBar
              value={search}
              onChange={(value) => setSearch(value)}
              onSubmit={goToSearch}
            />
            <div className="flex items-center gap-4 text-sm text-slate-600">
              <div className="flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-2 text-emerald-700">
                <span className="h-2 w-2 rounded-full bg-emerald-500" /> Live backend
              </div>
              <Link className="font-semibold text-emerald-700 hover:text-emerald-800" to="/auth">
                Create an account →
              </Link>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            {featured.map((property) => (
              <PropertyCard
                key={property.id}
                isFavorite={favorites.has(property.id)}
                onToggleFavorite={toggle}
                property={property}
              />
            ))}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-slate-900">Featured listings</h2>
          <Link className="text-sm font-semibold text-emerald-700 hover:text-emerald-800" to="/search">
            View all →
          </Link>
        </div>
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {featured.map((property) => (
            <PropertyCard
              key={property.id}
              isFavorite={favorites.has(property.id)}
              onToggleFavorite={toggle}
              property={property}
            />
          ))}
          {featured.length === 0 && (
            <p className="text-sm text-slate-600">No listings available yet. Try again shortly.</p>
          )}
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-semibold text-slate-900">Upcoming open houses</h2>
          <Link className="text-sm font-semibold text-emerald-700 hover:text-emerald-800" to="/search">
            Browse listings →
          </Link>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {openHouses.map((openHouse) => {
            const startDate = new Date(openHouse.startsAt)
            const endDate = new Date(openHouse.endsAt)
            const formattedDate = startDate.toLocaleDateString('sv-SE', { weekday: 'short', month: 'short', day: 'numeric' })
            const formattedTime = `${startDate.toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })} – ${endDate.toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })}`
            const cardContent = (
              <>
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">
                  <span>{openHouse.type}</span>
                  <span>{formattedDate}</span>
                </div>
                <div className="mt-3 text-lg font-semibold text-slate-900">{formattedTime}</div>
                {openHouse.note && <p className="mt-2 text-sm text-slate-600">{openHouse.note}</p>}
                {!openHouse.note && <p className="mt-2 text-sm text-slate-500">Detaljer saknas</p>}
              </>
            )

            if (openHouse.listingId) {
              return (
                <Link
                  key={openHouse.id}
                  to={`/property/${openHouse.listingId}`}
                  className="group rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100 transition hover:-translate-y-0.5 hover:shadow-md"
                >
                  {cardContent}
                </Link>
              )
            }

            return (
              <div
                key={openHouse.id}
                className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100"
              >
                {cardContent}
              </div>
            )
          })}
          {openHouses.length === 0 && (
            <p className="text-sm text-slate-600">No open houses announced right now. Check back soon.</p>
          )}
        </div>
      </section>
    </div>
  )
}
