import { useState, type FormEvent } from 'react'
import { BASE_URL } from '../api/client'

export function AuthPage() {
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [username, setUsername] = useState("test@example.com");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");


  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");

    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);

    try {
      const res = await fetch(`${BASE_URL}/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body,
      });

      if (!res.ok) {
        throw new Error("Wrong username or password");
      }

      const data = await res.json();
      console.log(data)
      const token = data.access_token
      localStorage.setItem("token", token);

      // const responce = await fetch(`${BASE_URL}/get/me`, {
      //   headers: {
      //     Authorization: `Bearer ${token}`,
      //   },
      // });
      // if (responce.ok) {
      //   const data = await responce.json();
      //   console.log(data)
      // }

    } catch (err) {
      setError((err as Error).message || "Something went wrong");
    }
  };

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

      <form className="space-y-4" onSubmit={handleSubmit}>
        {mode === 'register' && (
          <div className="space-y-1">
            <label className="text-sm font-semibold text-slate-800">Full name</label>
            <input className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Anna Andersson" />
          </div>
        )}

        {error && <p style={{ color: "red" }}>{error}</p>}

        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-800">Email</label>
          <input
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="you@example.com" type="email"
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="space-y-1">
          <label className="text-sm font-semibold text-slate-800">Password</label>
          <input
            className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm"
            placeholder="••••••••" type="password"
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <button
          className="w-full rounded-full bg-emerald-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
          type="submit"
        >
          {mode === 'login' ? 'Login' : 'Create account'}
        </button>
        <p className="text-xs text-slate-500">
          Hook this form to FastAPI auth endpoints. Persist tokens in HttpOnly cookies or secure storage once backend is connected.
        </p>
      </form>
    </div>
  )
}
