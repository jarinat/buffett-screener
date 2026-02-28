import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Buffett Screener',
  description: 'Value investing stock screener inspired by Warren Buffett principles',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
