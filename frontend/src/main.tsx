import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import { SwiftnoteApp } from './SwiftnoteApp'

import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <SwiftnoteApp />
  </StrictMode>,
)
