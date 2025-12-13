import { useState, type FormEvent } from 'react'
import { BASE_URL } from '../api/client'
import { useAuth } from '../context/AuthContext'

export function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState('anna.lindqvist@email.se')
  const [password, setPassword] = useState('1234')
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [phone, setPhone] = useState('')
  const [role, setRole] = useState<'buyer' | 'seller' | 'agent'>('buyer')
  const [streetAddress, setStreetAddress] = useState('')
  const [postalCode, setPostalCode] = useState('')
  const [city, setCity] = useState('')
  const [municipality, setMunicipality] = useState('')
  const [county, setCounty] = useState('')
  const [country, setCountry] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')
  const { login, logout, isAuthenticated, userId, error: authError } = useAuth()

  const authenticate = async () => {
    const body = new URLSearchParams()
    body.append('username', username)
    body.append('password', password)

    const res = await fetch(`${BASE_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body,
    })

    if (!res.ok) {
      throw new Error('Wrong username or password')
    }

    const data = await res.json()
    const token = data.access_token
    login(token)
  }

  const registerUser = async () => {
    const hasAddress = [streetAddress, postalCode, city, municipality, county, country].some((value) => value.trim().length > 0)
    let addressId: number | undefined

    if (hasAddress) {
      if (!streetAddress || !postalCode || !city || !country) {
        throw new Error('Please fill street, postal code, city and country or leave address blank')
      }

      const addressRes = await fetch(`${BASE_URL}/users/addresses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          street_address: streetAddress,
          postal_code: postalCode,
          city,
          municipality: municipality || undefined,
          county: county || undefined,
          country,
        }),
      })

      if (!addressRes.ok) {
        const message = await addressRes.text()
        throw new Error(message || 'Failed to save address')
      }

      const addressData: { id?: number } = await addressRes.json()
      addressId = addressData?.id
    }

    const userRes = await fetch(`${BASE_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: username,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
        phone: phone || undefined,
        role_name: role,
        address_id: addressId,
      }),
    })

    if (!userRes.ok) {
      const message = await userRes.text()
      throw new Error(message || 'Failed to create account')
    }

    await authenticate()
  }

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      if (mode === 'login') {
        await authenticate()
      } else {
        await registerUser()
      }
    } catch (err) {
      setError((err as Error).message || 'Something went wrong')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 rounded-3xl bg-white p-8 shadow-sm ring-1 ring-slate-100">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-emerald-700">Account</p>
          <h1 className="text-2xl font-semibold text-slate-900">{mode === 'login' ? 'Welcome back' : 'Create an account'}</h1>
        </div>
        <div className="flex gap-2">
          <button
            className={`rounded-full px-3 py-1 text-sm font-semibold transition ${mode === 'login' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-700'
              }`}
            onClick={() => setMode('login')}
            type="button"
          >
            Login
          </button>
          <button
            className={`rounded-full px-3 py-1 text-sm font-semibold transition ${mode === 'register' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-700'
              }`}
            onClick={() => setMode('register')}
            type="button"
          >
            Register
          </button>
        </div>
      </div>

      {isAuthenticated && (
        <div className="flex items-center justify-between rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-800">
          <span>{username || (userId ? `Logged in as user ${userId}` : 'Logged in')}</span>
          <button
            className="rounded-full border border-emerald-600 px-3 py-1 text-emerald-700 transition hover:bg-white"
            onClick={logout}
            type="button"
          >
            Logout
          </button>
        </div>
      )}

      <form className="space-y-4" onSubmit={handleSubmit}>
        {mode === 'register' && (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-800">First name</label>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Anna"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-800">Last name</label>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="Andersson"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-800">Phone</label>
              <input
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                placeholder="070-000 00 00"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
            <div className="space-y-1">
              <label className="text-sm font-semibold text-slate-800">Role</label>
              <select
                className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                value={role}
                onChange={(e) => setRole(e.target.value as 'buyer' | 'seller' | 'agent')}
              >
                <option value="buyer">Buyer</option>
                <option value="seller">Seller</option>
                <option value="agent">Agent</option>
              </select>
            </div>
            <div className="sm:col-span-2">
              <p className="text-xs font-semibold uppercase tracking-[0.1em] text-emerald-700">Address (optional)</p>
              <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <div className="space-y-1 sm:col-span-2">
                  <label className="text-sm font-semibold text-slate-800">Street address</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Storgatan 1"
                    value={streetAddress}
                    onChange={(e) => setStreetAddress(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-800">Postal code</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="123 45"
                    value={postalCode}
                    onChange={(e) => setPostalCode(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-800">City</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Stockholm"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-800">Municipality</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Norrmalm"
                    value={municipality}
                    onChange={(e) => setMunicipality(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-800">County</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Stockholms län"
                    value={county}
                    onChange={(e) => setCounty(e.target.value)}
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-sm font-semibold text-slate-800">Country</label>
                  <input
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
                    placeholder="Sweden"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {(error || authError) && <p className="text-sm text-red-600">{error || authError}</p>}

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-800">Email</label>
          <input
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="you@example.com" type="email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-800">Password</label>
          <input
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="••••••••" type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button
          className="w-full rounded-full bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
          type="submit"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Submitting...' : mode === 'login' ? 'Login' : 'Create account'}
        </button>
        <p className="text-xs text-slate-500">
          Hook this form to FastAPI auth endpoints. Persist tokens in HttpOnly cookies or secure storage once backend is connected.
        </p>
      </form>
    </div>
  )
}
