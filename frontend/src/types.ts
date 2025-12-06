export type Property = {
  id: string
  title: string
  address: string
  price: number
  rooms: number
  area: number
  type: string
  image: string
  images: string[]
  description: string
  broker: {
    name: string
    phone: string
  }
  tags?: string[]
  isFavorite?: boolean
  status?: string
  image_url?: string
}
