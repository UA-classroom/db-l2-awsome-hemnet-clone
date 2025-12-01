import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { deleteFavoriteListing, fetchSavedListings, saveFavoriteListing } from '../api/client'

const FavoritesContext = createContext<{
  favorites: Set<string>
  toggle: (id: string) => void
}>({
  favorites: new Set(),
  toggle: () => undefined,
})

const DEFAULT_USER_ID = '1' // TODO: wire to real auth user

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  useEffect(() => {
    let cancelled = false
    fetchSavedListings(DEFAULT_USER_ID).then((items) => {
      if (cancelled) return
      setFavorites(new Set(items))
    })
    return () => {
      cancelled = true
    }
  }, [])

  const toggle = useCallback((id: string) => {
    const wasFavorite = favorites.has(id)

    setFavorites((prev) => {
      const next = new Set(prev)
      if (wasFavorite) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })

    ;(async () => {
      try {
        if (wasFavorite) {
          await deleteFavoriteListing(DEFAULT_USER_ID, id)
        } else {
          await saveFavoriteListing(DEFAULT_USER_ID, id)
        }
      } catch (error) {
        console.error('Favorite toggle failed', error)
        // revert on error
        setFavorites((prev) => {
          const next = new Set(prev)
          if (wasFavorite) {
            next.add(id)
          } else {
            next.delete(id)
          }
          return next
        })
      }
    })()
  }, [favorites])

  const value = useMemo(() => ({ favorites, toggle }), [favorites, toggle])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFavorites() {
  return useContext(FavoritesContext)
}
