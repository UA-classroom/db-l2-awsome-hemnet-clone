import { HeartIcon, HomeIcon } from '@heroicons/react/24/outline'
import { Link, NavLink } from 'react-router-dom'

const navClasses = ({ isActive }: { isActive: boolean }) =>
  `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold transition ${isActive ? 'bg-emerald-50 text-emerald-700' : 'text-slate-700 hover:bg-slate-100'
  }`

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-50 via-white to-slate-50 text-slate-900">
      <header className="sticky top-0 z-20 border-b border-slate-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
          <Link className="flex items-center gap-2 text-lg font-bold text-emerald-700" to="/">
            <HomeIcon className="h-6 w-6" /> Hemnet Clone
          </Link>
          <nav className="flex items-center gap-2">
            <NavLink className={navClasses} to="/search">
              Search
            </NavLink>
            <NavLink className={navClasses} to="/favorites">
              <HeartIcon className="h-4 w-4" /> Favorites
            </NavLink>
            <NavLink className={navClasses} to="/auth">
              Login
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-5 py-8 lg:py-12">{children}</main>
      <footer className="border-t border-slate-100 bg-white/80 py-6 text-center text-sm text-slate-500">
        Built with React, Tailwind, and FastAPI backend
      </footer>
    </div>
  )
}
