import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Uplit - AI-Powered Restaurant Marketing',
  description: 'Transform your restaurant with intelligent automation. Advanced AI marketing platform designed exclusively for restaurants.',
  keywords: 'restaurant marketing, AI automation, restaurant growth, digital marketing, restaurant technology',
  authors: [{ name: 'Uplit Technologies' }],
  creator: 'Uplit Technologies',
  publisher: 'Uplit Technologies',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://uplit.app'),
  openGraph: {
    title: 'Uplit - AI-Powered Restaurant Marketing',
    description: 'Transform your restaurant with intelligent automation. Advanced AI marketing platform designed exclusively for restaurants.',
    url: 'https://uplit.app',
    siteName: 'Uplit',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'Uplit - AI-Powered Restaurant Marketing',
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Uplit - AI-Powered Restaurant Marketing',
    description: 'Transform your restaurant with intelligent automation. Advanced AI marketing platform designed exclusively for restaurants.',
    images: ['/og-image.png'],
    creator: '@UplitTech',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'your-google-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="icon" href="/favicon.ico" />
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#3b82f6" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
      </head>
      <body className="min-h-screen bg-[var(--bg-primary)] text-[var(--text-primary)] antialiased">
        <div id="root" className="min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
