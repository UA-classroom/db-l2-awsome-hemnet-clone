import { CalendarDaysIcon, MapPinIcon, PhoneIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { fetchListingMedia, fetchListingOpenHouses, fetchProperties, fetchProperty } from '../api/client'
import { ImageGallery } from '../components/ImageGallery'
import { PropertyCard } from '../components/PropertyCard'
import { useFavorites } from '../context/FavoritesContext'
import type { OpenHouse, Property } from '../types'

export function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { favorites, toggle } = useFavorites()
  const [property, setProperty] = useState<Property | null>(null)
  const [otherHomes, setOtherHomes] = useState<Property[]>([])
  const [loading, setLoading] = useState(true)
  const [images, setImages] = useState<string[]>([])
  const [openHouses, setOpenHouses] = useState<OpenHouse[]>([])

  useEffect(() => {
    if (!id) return
    let cancelled = false
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setLoading(true)

    fetchProperty(id).then((data) => {
      if (!cancelled) setProperty(data)
      if (data) {
        fetchListingMedia(id).then((media) => {
          if (!cancelled) setImages(media.length > 0 ? media : data.images)
        })
      }
    })
    fetchListingOpenHouses(id).then((items) => {
      if (!cancelled) setOpenHouses(items)
    })
    fetchProperties({ limit: 4, status: 'for_sale' }).then((data) => {
      if (cancelled) return
      setOtherHomes(data.filter((item) => item.id !== id).slice(0, 3))
    })
    return () => {
      cancelled = true
    }
  }, [id])

  if (!property && !loading) {
    return <p className="text-sm text-slate-600">Listing not found. Please go back to search.</p>
  }

  return (
    <div className="space-y-10">
      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          {property ? (
            <ImageGallery images={images.length ? images : property.images} />
          ) : (
            <div className="h-96 w-full animate-pulse rounded-3xl bg-slate-200" />
          )}
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
            {property ? (
              <>
                <h1 className="text-3xl font-semibold text-slate-900">{property.title}</h1>
                <div className="mt-2 flex flex-wrap items-center gap-3 text-sm text-slate-600">
                  <span className="rounded-full bg-emerald-50 px-3 py-1 font-semibold text-emerald-700">
                    {property.price.toLocaleString('sv-SE')} kr
                  </span>
                  <span>{property.rooms} rooms</span>
                  <span className="text-slate-300">•</span>
                  <span>{property.area} sqm</span>
                  <span className="text-slate-300">•</span>
                  <span className="inline-flex items-center gap-2">
                    <MapPinIcon className="h-4 w-4 text-emerald-500" /> {property.address}
                  </span>
                </div>
                <p className="mt-4 text-slate-700">{property.description}</p>
                {property.tags && (
                  <div className="mt-4 flex flex-wrap gap-2 text-xs text-emerald-700">
                    {property.tags.map((tag) => (
                      <span key={tag} className="rounded-full bg-emerald-50 px-3 py-1 font-semibold">
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                {openHouses.length > 0 && (
                  <div className="mt-6 rounded-2xl bg-emerald-50/80 p-4 ring-1 ring-emerald-100">
                    <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.2em] text-emerald-800">
                      <CalendarDaysIcon className="h-4 w-4" />
                      Kommande visningar
                    </div>
                    <div className="mt-3 space-y-3">
                      {openHouses.map((item) => {
                        const startDate = new Date(item.startsAt)
                        const endDate = new Date(item.endsAt)
                        const formattedDate = startDate.toLocaleDateString('sv-SE', {
                          weekday: 'short',
                          month: 'short',
                          day: 'numeric',
                        })
                        const formattedTime = `${startDate.toLocaleTimeString('sv-SE', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })} – ${endDate.toLocaleTimeString('sv-SE', { hour: '2-digit', minute: '2-digit' })}`
                        return (
                          <div key={item.id} className="rounded-xl bg-white p-3 shadow-sm ring-1 ring-emerald-100/70">
                            <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700">
                              <span>{item.type}</span>
                              <span>{formattedDate}</span>
                            </div>
                            <div className="mt-2 text-base font-semibold text-slate-900">{formattedTime}</div>
                            {item.note && <p className="mt-1 text-sm text-slate-700">{item.note}</p>}
                          </div>
                        )
                      })}
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-sm text-slate-600">Loading listing details…</p>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Broker</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-900">{property?.broker.name ?? 'Loading...'}</h3>
            <p className="text-sm text-slate-600">Call to book a viewing.</p>
            <button
              className="mt-4 inline-flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
              disabled={!property}
              type="button"
            >
              <PhoneIcon className="h-4 w-4" /> {property?.broker.phone ?? 'Pending'}
            </button>
            <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-xs text-slate-600">
              Map placeholder — coordinates not provided yet.
            </div>
          </div>

          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
            <h4 className="text-lg font-semibold text-slate-900">Similar homes</h4>
            <div className="mt-4 grid gap-4">
              {otherHomes.map((item) => (
                <PropertyCard
                  key={item.id}
                  isFavorite={favorites.has(item.id)}
                  onToggleFavorite={toggle}
                  property={item}
                />
              ))}
              {otherHomes.length === 0 && <p className="text-sm text-slate-600">Loading nearby listings…</p>}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
