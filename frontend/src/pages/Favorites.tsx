import { HeartIcon } from '@heroicons/react/24/outline'
import { PropertyCard } from '../components/PropertyCard'
import { useFavorites } from '../context/FavoritesContext'
import { mockProperties } from '../data/mockProperties'

export function FavoritesPage() {
  const { favorites, toggle } = useFavorites()
  const saved = mockProperties.filter((property) => favorites.has(property.id))

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <HeartIcon className="h-5 w-5 text-emerald-600" />
        <h1 className="text-2xl font-semibold text-slate-900">My Favorites</h1>
      </div>
      {saved.length === 0 ? (
        <div className="rounded-3xl bg-white p-6 text-sm text-slate-600 shadow-sm ring-1 ring-slate-100">
          No saved homes yet. Browse search results and tap the heart to save.
        </div>
      ) : (
        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {saved.map((property) => (
            <PropertyCard
              key={property.id}
              isFavorite
              onToggleFavorite={toggle}
              property={property}
            />
          ))}
        </div>
      )}
    </div>
  )
}
