import React from 'react'
import { Languages, Sparkles } from 'lucide-react'

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <div className="navbar-brand">
          <div className="brand-icon">
            <Languages size={20} />
          </div>
          <div>
            <div className="brand-title">IndicTranslate</div>
            <div className="brand-subtitle">English to Regional Language Neural Machine Translation</div>
          </div>
        </div>
      </div>
    </nav>
  )
}
