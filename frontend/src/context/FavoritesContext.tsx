import { createContext, type ReactNode, useCallback, useContext, useMemo, useState } from 'react'

const FavoritesContext = createContext<{
  favorites: Set<string>
  toggle: (id: string) => void
}>({
  favorites: new Set(),
  toggle: () => undefined,
})

export function FavoritesProvider({ children }: { children: ReactNode }) {
  const [favorites, setFavorites] = useState<Set<string>>(new Set())

  const toggle = useCallback((id: string) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  const value = useMemo(() => ({ favorites, toggle }), [favorites, toggle])

  return <FavoritesContext.Provider value={value}>{children}</FavoritesContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useFavorites() {
  return useContext(FavoritesContext)
}
