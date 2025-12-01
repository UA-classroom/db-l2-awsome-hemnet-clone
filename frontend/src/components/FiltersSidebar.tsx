import { AdjustmentsVerticalIcon } from '@heroicons/react/24/outline'
import { useMemo } from 'react'
import { PriceRangeSlider } from './PriceRangeSlider'

export type FilterState = {
  location: string
  price: [number, number]
  minRooms: number
  propertyTypes: string[]
}

type Props = {
  filters: FilterState
  onChange: (next: FilterState) => void
}

const propertyTypeOptions = ['Apartment', 'Villa', 'Townhouse', 'New development']

export function FiltersSidebar({ filters, onChange }: Props) {
  const toggleType = (type: string) => {
    const nextTypes = filters.propertyTypes.includes(type)
      ? filters.propertyTypes.filter((item) => item !== type)
      : [...filters.propertyTypes, type]
    onChange({ ...filters, propertyTypes: nextTypes })
  }

  const summary = useMemo(() => {
    const roomText = filters.minRooms > 0 ? `${filters.minRooms}+ rooms` : 'Any rooms'
    const typeText = filters.propertyTypes.length ? filters.propertyTypes.join(', ') : 'Any type'
    return `${roomText} · ${typeText}`
  }, [filters.minRooms, filters.propertyTypes])

  return (
    <aside className="space-y-4 rounded-3xl bg-slate-50 p-5 shadow-inner ring-1 ring-slate-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-900">Filters</p>
          <p className="text-xs text-slate-500">{summary}</p>
        </div>
        <AdjustmentsVerticalIcon className="h-5 w-5 text-emerald-600" />
      </div>

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Location</label>
        <input
          className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500"
          placeholder="City or area"
          value={filters.location}
          onChange={(e) => onChange({ ...filters, location: e.target.value })}
        />
      </div>

      <PriceRangeSlider min={1500000} max={12000000} value={filters.price} onChange={(price) => onChange({ ...filters, price })} />

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Rooms</label>
        <div className="flex gap-2">
          {[0, 1, 2, 3, 4, 5].map((rooms) => (
            <button
              key={rooms}
              className={`rounded-full px-3 py-1 text-sm font-semibold transition ${filters.minRooms === rooms ? 'bg-emerald-600 text-white' : 'bg-white text-slate-700 ring-1 ring-slate-200 hover:ring-emerald-200'}`}
              onClick={() => onChange({ ...filters, minRooms: rooms })}
              type="button"
            >
              {rooms === 0 ? 'Any' : `${rooms}+`}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Type</label>
        <div className="grid grid-cols-2 gap-2">
          {propertyTypeOptions.map((type) => (
            <label key={type} className="flex cursor-pointer items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm ring-1 ring-slate-200 transition hover:ring-emerald-200">
              <input
                checked={filters.propertyTypes.includes(type)}
                className="accent-emerald-600"
                type="checkbox"
                onChange={() => toggleType(type)}
              />
              <span>{type}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  )
}
