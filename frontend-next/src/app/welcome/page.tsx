import { ThemeProvider } from '../../contexts/ThemeContext'
import { AuthProvider } from '../../contexts/AuthContext'
import WelcomeToFreedom from '../../components/WelcomeToFreedom'

export default function WelcomePage() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <WelcomeToFreedom />
      </AuthProvider>
    </ThemeProvider>
  )
}