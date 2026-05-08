import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { SwiftnoteApp } from './SwiftnoteApp'
import { GoogleOAuthProvider } from "@react-oauth/google"

import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID as string}>
      <SwiftnoteApp />
    </GoogleOAuthProvider>
  </StrictMode>
)
