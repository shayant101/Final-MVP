import { ThemeProvider } from '../../contexts/ThemeContext'
import { AuthProvider } from '../../contexts/AuthContext'
import EmailVerificationSuccess from '../../components/EmailVerificationSuccess'

export default function VerifyEmailPage() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <EmailVerificationSuccess />
      </AuthProvider>
    </ThemeProvider>
  )
}