import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'

// Asegurar encoding UTF-8
document.documentElement.lang = 'es-GT'
document.documentElement.setAttribute('charset', 'UTF-8')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>
)
