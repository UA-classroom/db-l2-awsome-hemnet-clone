import { useState } from 'react'

export function ImageGallery({ images }: { images: string[] }) {
  const [active, setActive] = useState(0)

  return (
    <div className="space-y-3">
      <div className="overflow-hidden rounded-3xl border border-slate-100">
        <img alt="Property" className="h-96 w-full object-cover" src={images[active]} />
      </div>
      <div className="flex gap-3 overflow-x-auto pb-1">
        {images.map((src, index) => (
          <button
            key={src}
            className={`h-20 w-28 flex-shrink-0 overflow-hidden rounded-xl border transition ${index === active ? 'border-emerald-500' : 'border-slate-100 hover:border-emerald-200'}`}
            onClick={() => setActive(index)}
            type="button"
          >
            <img alt="Thumbnail" className="h-full w-full object-cover" src={src} />
          </button>
        ))}
      </div>
    </div>
  )
}
