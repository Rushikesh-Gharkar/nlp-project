import React, { useState, useEffect } from 'react'
import Translator from '../components/Translator'
import TranslationHistory from '../components/TranslationHistory'
import AboutSection from '../components/AboutSection'

const STORAGE_KEY = 'indic_translator_history_v1'

export default function Home({ initialText = '' }) {
  const [history, setHistory] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })

  const [prefilledText, setPrefilledText] = useState(initialText)

  useEffect(() => {
    if (initialText) {
      setPrefilledText(initialText)
    }
  }, [initialText])

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history))
    } catch (e) {
      console.warn('Failed to save translation history to localStorage', e)
    }
  }, [history])

  const handleTranslationComplete = (newEntry) => {
    setHistory((prev) => [newEntry, ...prev.slice(0, 19)]) // store up to 20 recent items
  }

  const handleClearHistory = () => {
    setHistory([])
    localStorage.removeItem(STORAGE_KEY)
  }

  const handleSelectHistoryItem = (item) => {
    setPrefilledText(item.sourceText)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <div>
      <Translator
        onTranslationComplete={handleTranslationComplete}
        defaultSourceText={prefilledText}
      />

      <TranslationHistory
        history={history}
        onClearHistory={handleClearHistory}
        onSelectHistoryItem={handleSelectHistoryItem}
      />

      <AboutSection />
    </div>
  )
}
