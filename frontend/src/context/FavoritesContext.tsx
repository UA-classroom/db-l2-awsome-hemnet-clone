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
  const { userId, isAuthenticated, token } = useAuth()
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  useEffect(() => {
    setFavorites(new Set())
    if (!isAuthenticated || !userId || !token) return

    let cancelled = false
    fetchSavedListings(userId, token).then((items) => {
      if (cancelled) return
      setFavorites(new Set(items))
    })
    return () => {
      cancelled = true
    }
  }, [isAuthenticated, token, userId])

  const toggle = useCallback((id: string) => {
    if (!isAuthenticated || !userId || !token) {
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
          await deleteFavoriteListing(userId, id, token)
        } else {
          await saveFavoriteListing(userId, id, token)
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
  }, [favorites, isAuthenticated, token, userId])

  const value = useMemo(() => ({ favorites, toggle }), [favorites, toggle])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFavorites() {
  return useContext(FavoritesContext)
}
