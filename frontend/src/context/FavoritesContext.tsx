import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { deleteFavoriteListing, fetchSavedListings, saveFavoriteListing } from '../api/client'
import { useAuth } from './AuthContext'

const FavoritesContext = createContext<{
  favorites: Set<string>
  toggle: (id: string) => void
}>({
  favorites: new Set(),
  toggle: () => undefined,
})

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const { userId, isAuthenticated } = useAuth()
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  useEffect(() => {
    setFavorites(new Set())
    if (!isAuthenticated || !userId) return

    let cancelled = false
    fetchSavedListings(userId).then((items) => {
      if (cancelled) return
      setFavorites(new Set(items))
    })
    return () => {
      cancelled = true
    }
  }, [isAuthenticated, userId])

  const toggle = useCallback((id: string) => {
    if (!isAuthenticated || !userId) {
      console.warn('Favorites toggle ignored: no authenticated user.')
      return
    }

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
          await deleteFavoriteListing(userId, id)
        } else {
          await saveFavoriteListing(userId, id)
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
  }, [favorites, isAuthenticated, userId])

  const value = useMemo(() => ({ favorites, toggle }), [favorites, toggle])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFavorites() {
  return useContext(FavoritesContext)
}
