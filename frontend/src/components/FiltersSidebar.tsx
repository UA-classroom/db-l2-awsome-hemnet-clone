import { AdjustmentsVerticalIcon } from '@heroicons/react/24/outline'
import { useMemo } from 'react'
import { PriceRangeSlider } from './PriceRangeSlider'

export type FilterState = {
  location: string
  price: [number, number]
  minRooms: number
  maxRooms: number
  propertyTypes: string[]
  status?: string
}

type Props = {
  filters: FilterState
  onChange: (next: FilterState) => void
}

const propertyTypeOptions = [
  { label: 'Apartment', value: 'apartment' },
  { label: 'House', value: 'house' },
  { label: 'Townhouse', value: 'townhouse' },
  { label: 'Vacation home', value: 'vacation_home' },
  { label: 'Farm', value: 'farm' },
  { label: 'Other', value: 'other' },
]

export function FiltersSidebar({ filters, onChange }: Props) {
  const toggleType = (type: string) => {
    const nextTypes = filters.propertyTypes.includes(type)
      ? filters.propertyTypes.filter((item) => item !== type)
      : [...filters.propertyTypes, type]
    onChange({ ...filters, propertyTypes: nextTypes })
  }

  const summary = useMemo(() => {
    const minLabel = filters.minRooms === 0 ? 'Any' : filters.minRooms
    const maxLabel = filters.maxRooms === Infinity || filters.maxRooms === 0 ? 'Any' : filters.maxRooms
    const roomText = minLabel === 'Any' && maxLabel === 'Any' ? 'Any rooms' : `${minLabel}–${maxLabel} rooms`
    const typeText = filters.propertyTypes.length ? filters.propertyTypes.join(', ') : 'Any type'
    return `${roomText} · ${typeText}`
  }, [filters.minRooms, filters.maxRooms, filters.propertyTypes])

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

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-800">Min rooms</label>
          <input
            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500"
            min={0}
            type="number"
            value={filters.minRooms === 0 ? '' : filters.minRooms}
            placeholder="Any"
            onChange={(e) => {
              const value = e.target.value === '' ? 0 : Number(e.target.value)
              onChange({ ...filters, minRooms: value })
            }}
          />
        </div>
        <div className="space-y-2">
          <label className="text-sm font-semibold text-slate-800">Max rooms</label>
          <input
            className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm outline-none focus:border-emerald-500"
            min={0}
            type="number"
            value={filters.maxRooms === Infinity ? '' : filters.maxRooms}
            placeholder="Any"
            onChange={(e) => {
              const raw = e.target.value === '' ? Infinity : Number(e.target.value)
              const value = raw === 0 ? Infinity : raw
              onChange({ ...filters, maxRooms: value })
            }}
          />
        </div>
      </div>

      <div className="space-y-2">
        <label className="text-sm font-semibold text-slate-800">Type</label>
        <div className="grid grid-cols-2 gap-2">
          {propertyTypeOptions.map((type) => (
            <label key={type.value} className="flex cursor-pointer items-center gap-2 rounded-xl bg-white px-3 py-2 text-sm ring-1 ring-slate-200 transition hover:ring-emerald-200">
              <input
                checked={filters.propertyTypes.includes(type.value)}
                className="accent-emerald-600"
                type="checkbox"
                onChange={() => toggleType(type.value)}
              />
              <span>{type.label}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  )
}
