const BASE_URL = 'http://127.1.1.1:8000'

export async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...init,
  })

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status}`)
  }

  return res.json() as Promise<T>
}

export async function getProperties(query: Record<string, string | number | undefined>) {
  const params = new URLSearchParams()
  Object.entries(query).forEach(([key, value]) => {
    if (value !== undefined) params.append(key, String(value))
  })
  // Swap endpoint path when backend exposes listings route
  return fetchJson(`/properties?${params.toString()}`)
}

export { BASE_URL }
