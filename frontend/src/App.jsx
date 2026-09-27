import React from 'react'
import Navbar from './components/Navbar'
import Home from './pages/Home'

export default function App() {
  return (
    <div className="app-container">
      <Navbar />

      <main className="main-content">
        <Home />
      </main>

      <footer className="footer">
        <p>
          IndicTranslate • English to Regional Language Neural Machine Translation • Helsinki-NLP MarianMT
        </p>
      </footer>
    </div>
  )
}
