import type { Property } from '../types'

export const mockProperties: Property[] = [
  {
    id: 'stockholm-vasastan-01',
    title: 'Luminous 2BR with Balcony',
    address: 'Sveavägen 14, Vasastan, Stockholm',
    price: 5450000,
    rooms: 2,
    area: 58,
    type: 'Apartment',
    image: 'https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1200&q=80',
    images: [
      'https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1400&q=80',
      'https://images.unsplash.com/photo-1505691723518-36a5ac3be353?auto=format&fit=crop&w=1400&q=80',
      'https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1400&q=80',
    ],
    description: 'Bright top-floor apartment with south-facing balcony, herringbone floors, and generous storage. Minutes to Odenplan.',
    broker: {
      name: 'Elin Larsson',
      phone: '+46 70 555 12 34',
    },
    tags: ['Balcony', 'Top floor', 'Renovated'],
    isFavorite: true,
    coordinates: { lat: 59.344, lng: 18.058 },
  },
  {
    id: 'stockholm-sodermalm-02',
    title: 'Minimalist Studio by Mariatorget',
    address: 'Bastugatan 22, Södermalm, Stockholm',
    price: 3295000,
    rooms: 1,
    area: 34,
    type: 'Apartment',
    image: 'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=1200&q=80',
    images: [
      'https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?auto=format&fit=crop&w=1400&q=80',
      'https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1400&q=80',
    ],
    description: 'Clean lines, large windows, and built-ins. Perfect pied-à-terre close to cafés and water.',
    broker: {
      name: 'Johan Ek',
      phone: '+46 73 111 22 44',
    },
    tags: ['High ceiling', 'Walk-in closet'],
    coordinates: { lat: 59.318, lng: 18.056 },
  },
  {
    id: 'goteborg-linne-03',
    title: 'Family 3BR near Slottsskogen',
    address: 'Prinsgatan 7, Linné, Göteborg',
    price: 6150000,
    rooms: 3,
    area: 92,
    type: 'Townhouse',
    image: 'https://images.unsplash.com/photo-1449844908441-8829872d2607?auto=format&fit=crop&w=1200&q=80',
    images: [
      'https://images.unsplash.com/photo-1449844908441-8829872d2607?auto=format&fit=crop&w=1400&q=80',
      'https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=1400&q=80',
    ],
    description: 'Open kitchen/living, double exposures, and park proximity. Basement storage and stroller room included.',
    broker: {
      name: 'Sara Nyström',
      phone: '+46 76 987 65 43',
    },
    tags: ['Family friendly', 'Park nearby'],
    coordinates: { lat: 57.696, lng: 11.949 },
  },
]
