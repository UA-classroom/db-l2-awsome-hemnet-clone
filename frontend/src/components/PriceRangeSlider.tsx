type Props = {
  min: number
  max: number
  value: [number, number]
  onChange: (value: [number, number]) => void
}

export function PriceRangeSlider({ min, max, value, onChange }: Props) {
  const [currentMin, currentMax] = value

  return (
    <div className="space-y-3 rounded-2xl bg-white p-4 shadow-sm ring-1 ring-slate-100">
      <div className="flex items-center justify-between text-sm text-slate-600">
        <span>Price range</span>
        <span className="font-semibold text-slate-900">
          {currentMin.toLocaleString('sv-SE')} kr - {currentMax.toLocaleString('sv-SE')} kr
        </span>
      </div>
      <div className="flex items-center gap-3">
        <input
          aria-label="Minimum price"
          className="w-full accent-emerald-600"
          max={max}
          min={min}
          step={50000}
          type="range"
          value={currentMin}
          onChange={(e) => onChange([Math.min(Number(e.target.value), currentMax - 50000), currentMax])}
        />
        <input
          aria-label="Maximum price"
          className="w-full accent-emerald-600"
          max={max}
          min={min}
          step={50000}
          type="range"
          value={currentMax}
          onChange={(e) => onChange([currentMin, Math.max(Number(e.target.value), currentMin + 50000)])}
        />
      </div>
    </div>
  )
}
