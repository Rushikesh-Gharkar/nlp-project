import React from 'react'
import { ArrowRight } from 'lucide-react'

export default function LanguageSelector({
  targetLanguage,
  setTargetLanguage,
  languages = [
    { code: 'hi', name: 'Hindi', native: 'हिन्दी' },
    { code: 'mr', name: 'Marathi', native: 'मराठी' },
  ],
}) {
  return (
    <div className="language-selector-group">
      <div className="lang-badge">
        <span>Source:</span>
        <strong>English (EN)</strong>
      </div>

      <ArrowRight size={16} color="#64748b" />

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.85rem', color: '#94a3b8', fontWeight: 600 }}>Target:</span>
        {languages.map((lang) => {
          const isActive = targetLanguage === lang.code
          return (
            <button
              key={lang.code}
              type="button"
              className={`lang-toggle-btn ${isActive ? 'active' : ''}`}
              onClick={() => setTargetLanguage(lang.code)}
            >
              <span>{lang.name}</span>
              <span style={{ opacity: 0.75, fontSize: '0.8rem' }}>({lang.native})</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
