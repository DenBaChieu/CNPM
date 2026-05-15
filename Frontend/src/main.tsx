import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from "react-router-dom"
import App from "./App"
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <div className="min-h-screen bg-linear-to-r from-purple-800 to-pink-800">
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </div>
  </StrictMode>,
)