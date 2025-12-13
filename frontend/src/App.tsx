import { Navigate, Route, Routes } from 'react-router-dom'
import { AppLayout } from './layouts/AppLayout'
import { AuthPage } from './pages/Auth'
import { FavoritesPage } from './pages/Favorites'
import { HomePage } from './pages/Home'
import { PropertyDetailPage } from './pages/PropertyDetail'
import { SearchResultsPage } from './pages/SearchResults'

function App() {
  return (
    <AppLayout>
      <Routes>
        <Route element={<HomePage />} path="/" />
        <Route element={<SearchResultsPage />} path="/search" />
        <Route element={<PropertyDetailPage />} path="/property/:id" />
        <Route element={<AuthPage />} path="/auth" />
        <Route element={<FavoritesPage />} path="/favorites" />
        <Route element={<Navigate replace to="/" />} path="*" />
      </Routes>
    </AppLayout>
  )
}

export default App
