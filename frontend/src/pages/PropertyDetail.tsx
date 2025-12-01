import { MapPinIcon, PhoneIcon } from '@heroicons/react/24/outline'
import { useMemo } from 'react'
import { useParams } from 'react-router-dom'
import { ImageGallery } from '../components/ImageGallery'
import { PropertyCard } from '../components/PropertyCard'
import { useFavorites } from '../context/FavoritesContext'
import { mockProperties } from '../data/mockProperties'

export function PropertyDetailPage() {
  const { id } = useParams<{ id: string }>()
  const { favorites, toggle } = useFavorites()

  const property = useMemo(() => mockProperties.find((item) => item.id === id), [id])
  const otherHomes = useMemo(() => mockProperties.filter((item) => item.id !== id).slice(0, 3), [id])

  if (!property) {
    return <p className="text-sm text-slate-600">Listing not found. Please go back to search.</p>
  }

  return (
    <div className="space-y-10">
      <div className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
        <div className="space-y-6">
          <ImageGallery images={property.images} />
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
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
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl bg-white p-6 shadow-sm ring-1 ring-slate-100">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Broker</p>
            <h3 className="mt-2 text-xl font-semibold text-slate-900">{property.broker.name}</h3>
            <p className="text-sm text-slate-600">Call to book a viewing.</p>
            <button
              className="mt-4 inline-flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
              type="button"
            >
              <PhoneIcon className="h-4 w-4" /> {property.broker.phone}
            </button>
            <div className="mt-6 rounded-2xl bg-slate-50 p-4 text-xs text-slate-600">
              Map placeholder ({property.coordinates?.lat?.toFixed(3)}, {property.coordinates?.lng?.toFixed(3)}) — replace with map embed when ready.
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
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
