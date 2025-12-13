import { HeartIcon, MapPinIcon } from '@heroicons/react/24/solid'
import { Link } from 'react-router-dom'
import type { Property } from '../types'

interface Props {
  property: Property
  isFavorite: boolean
  onToggleFavorite: (id: string) => void
}

export function PropertyCard({ property, isFavorite, onToggleFavorite }: Props) {
  const { id, title, address, price, rooms, area, image, tags } = property

  return (
    <article className="group flex flex-col overflow-hidden rounded-3xl border border-slate-100 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-xl">
      <div className="relative aspect-[4/3] overflow-hidden">
        <img alt={title} className="h-full w-full object-cover transition duration-500 group-hover:scale-105" src={image} />
        <button
          aria-label="Toggle favorite"
          className="absolute right-3 top-3 inline-flex items-center justify-center rounded-full bg-white/90 p-2 text-emerald-600 shadow-sm transition hover:bg-white"
          onClick={() => onToggleFavorite(id)}
          type="button"
        >
          <HeartIcon className={`h-5 w-5 ${isFavorite ? 'fill-emerald-600' : 'fill-white stroke-emerald-600'}`} />
        </button>
      </div>
      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-lg font-semibold text-slate-900">
            <Link className="transition hover:text-emerald-600" to={`/property/${id}`}>
              {title}
            </Link>
          </h3>
          <span className="text-sm font-semibold text-emerald-700">{price.toLocaleString('sv-SE')} kr</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-slate-600">
          <MapPinIcon className="h-4 w-4 text-emerald-500" />
          <span>{address}</span>
        </div>
        <div className="flex items-center gap-3 text-sm font-medium text-slate-800">
          <span>{rooms} rooms</span>
          <span className="text-slate-300">•</span>
          <span>{area} sqm</span>
        </div>
        {tags && (
          <div className="flex flex-wrap gap-2 text-xs text-emerald-700">
            {tags.map((tag) => (
              <span key={tag} className="rounded-full bg-emerald-50 px-3 py-1 font-semibold">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </article>
  )
}
