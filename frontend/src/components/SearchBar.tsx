import { MagnifyingGlassIcon, MapPinIcon } from '@heroicons/react/24/outline'
import { useEffect, useState } from 'react'
import { fetchAutocomplete } from '../api/client'

type Props = {
  value: string
  onChange: (value: string) => void
  onSubmit?: () => void
}

export function SearchBar({ value, onChange, onSubmit }: Props) {
  const [open, setOpen] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])

  useEffect(() => {
    if (!value.trim()) {
      setSuggestions([])
      return
    }

    let isActive = true
    const controller = new AbortController()
    const timeout = setTimeout(() => {
      fetchAutocomplete(value, controller.signal)
        .then((items) => {
          if (isActive) setSuggestions(items.slice(0, 10))
        })
        .catch((error) => {
          if (error instanceof Error && error.name === 'AbortError') return
          if (isActive) setSuggestions([])
        })
    }, 200)

    return () => {
      isActive = false
      controller.abort()
      clearTimeout(timeout)
    }
  }, [value])

  return (
    <div className="relative w-full max-w-3xl">
      <div className="flex items-center rounded-full border border-slate-200 bg-white px-4 py-3 shadow-sm transition hover:shadow-md">
        <MapPinIcon className="mr-3 h-5 w-5 text-emerald-600" />
        <input
          aria-label="Search location"
          className="w-full bg-transparent text-base outline-none placeholder:text-slate-400"
          placeholder="Search by city, address, or area"
          value={value}
          onFocus={() => setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 120)}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') onSubmit?.()
          }}
        />
        <button
          className="flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
          onClick={onSubmit}
          type="button"
        >
          <MagnifyingGlassIcon className="h-4 w-4" />
          Search
        </button>
      </div>
      {open && suggestions.length > 0 && (
        <div className="absolute left-0 right-0 z-10 mt-2 overflow-hidden rounded-2xl border border-slate-100 bg-white shadow-lg">
          <ul className="divide-y divide-slate-100">
            {suggestions.map((item) => (
              <li key={item}>
                <button
                  className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm text-slate-700 transition hover:bg-slate-50"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => {
                    onChange(item)
                    setOpen(false)
                    onSubmit?.()
                  }}
                  type="button"
                >
                  <MapPinIcon className="h-4 w-4 text-emerald-500" />
                  {item}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
