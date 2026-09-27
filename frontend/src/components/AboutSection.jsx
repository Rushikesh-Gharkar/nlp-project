import React from 'react'
import { Server, Zap, Globe2 } from 'lucide-react'

export default function AboutSection() {
  return (
    <div style={{ marginTop: '3rem' }}>
      <h2
        style={{
          fontSize: '1.25rem',
          fontWeight: 600,
          color: '#e2e8f0',
          marginBottom: '1.25rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
        }}
      >
        How it Works
      </h2>
      
      <div 
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {/* Feature 1 */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div 
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
            }}
          >
            <Globe2 size={20} color="#818cf8" />
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.5rem' }}>
            Local Processing
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
            Translations run entirely on your local machine using PyTorch and FastAPI, 
            ensuring complete privacy and offline capabilities.
          </p>
        </div>

        {/* Feature 2 */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div 
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(16, 185, 129, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
            }}
          >
            <Zap size={20} color="#10b981" />
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.5rem' }}>
            MarianMT Models
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
            Powered by Helsinki-NLP's Opus-MT neural models, specifically trained 
            on English to Indian regional language pairs.
          </p>
        </div>

        {/* Feature 3 */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div 
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              background: 'rgba(245, 158, 11, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '1rem',
            }}
          >
            <Server size={20} color="#f59e0b" />
          </div>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.5rem' }}>
            Dictionary Fallback
          </h3>
          <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>
            A smart dictionary cache provides immediate, accurate translations 
            for known dataset words before falling back to model inference.
          </p>
        </div>
      </div>
    </div>
  )
}
