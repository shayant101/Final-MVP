import { ThemeProvider } from '../../contexts/ThemeContext'
import { AuthProvider } from '../../contexts/AuthContext'
import MainDashboard from '../../components/MainDashboard'

export default function DashboardPage() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <MainDashboard />
      </AuthProvider>
    </ThemeProvider>
  )
}