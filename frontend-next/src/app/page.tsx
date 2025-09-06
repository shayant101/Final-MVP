import { ThemeProvider } from '../contexts/ThemeContext'
import { AuthProvider } from '../contexts/AuthContext'
import LandingPage from '../components/LandingPage'

export default function HomePage() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <LandingPage />
      </AuthProvider>
    </ThemeProvider>
  )
}
