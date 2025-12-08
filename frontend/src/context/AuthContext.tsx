import { createContext, type ReactNode, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { BASE_URL } from '../api/client'

type AuthContextValue = {
  token: string | null
  userId: number | null
  username: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
  login: (token: string) => void
  logout: () => void
}

const AuthContext = createContext<AuthContextValue>({
  token: null,
  userId: null,
  username: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  login: () => undefined,
  logout: () => undefined,
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [userId, setUserId] = useState<number | null>(null)
  const [username, setUsername] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const loadUser = useCallback(
    async (currentToken: string) => {
      setIsLoading(true)
      setError(null)
      try {
        const res = await fetch(`${BASE_URL}/users/me`, {
          headers: {
            Authorization: `Bearer ${currentToken}`,
          },
        })

        if (!res.ok) {
          throw new Error('Unauthorized')
        }

        const data = await res.json()
        const rawId = data.user_id
        const parsedId = typeof rawId === 'string' ? Number(rawId) : rawId
        setUserId(Number.isFinite(parsedId) ? parsedId : null)
        setUsername(data.username ?? null)
      } catch (err) {
        setUserId(null)
        setUsername(null)
        setToken(null)
        localStorage.removeItem('token')
        setError((err as Error).message || 'Session expired. Please log in again.')
      } finally {
        setIsLoading(false)
      }
    },
    [],
  )

  useEffect(() => {
    if (!token) {
      setUserId(null)
      setUsername(null)
      setError(null)
      return
    }

    loadUser(token)
  }, [loadUser, token])

  const login = useCallback((nextToken: string) => {
    setToken(nextToken)
    localStorage.setItem('token', nextToken)
    setError(null)
  }, [])

  const logout = useCallback(() => {
    setToken(null)
    setUserId(null)
    setUsername(null)
    setError(null)
    localStorage.removeItem('token')
  }, [])

  const isAuthenticated = Boolean(token)

  const value = useMemo(
    () => ({
      token,
      userId,
      username,
      isAuthenticated,
      isLoading,
      error,
      login,
      logout,
    }),
    [error, isAuthenticated, isLoading, login, logout, token, userId, username],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  return useContext(AuthContext)
}
