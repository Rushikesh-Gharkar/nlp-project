import React, { useState, useEffect } from 'react'
import {
  Send,
  Trash2,
  Copy,
  Check,
  Sparkles,
  Loader2,
  AlertCircle,
  Clock,
  Volume2,
  BookOpen,
} from 'lucide-react'
import LanguageSelector from './LanguageSelector'

const WORD_BANK_CATEGORIES = {
  verbs: {
    label: 'Actions & Verbs',
    words: [
      'eat', 'drink', 'read', 'write', 'learn', 'teach', 'speak', 'listen',
      'see', 'help', 'think', 'understand', 'know', 'work', 'study', 'sleep',
      'walk', 'run', 'sit', 'stand', 'open', 'close', 'start', 'buy', 'sell'
    ],
  },
  descriptors: {
    label: 'Everyday Words',
    words: [
      'good', 'bad', 'big', 'small', 'new', 'old', 'hot', 'cold', 'fast',
      'slow', 'easy', 'difficult', 'beautiful', 'happy', 'sad', 'clean', 'dirty'
    ],
  },
  sentences: {
    label: 'Conversations & Greetings',
    words: [
      'How are you?',
      'Good morning.',
      'Thank you.',
      'What is your name?',
      'Where do you live?',
      'Please help me.',
      'Have a nice day.'
    ],
  },
  tech: {
    label: 'NLP & Programming',
    words: [
      'I am learning machine learning.',
      'I am learning NLP.',
      'I like programming.',
      'The code has an error.',
      'The program is running.'
    ],
  },
}

export default function Translator({
  onTranslationComplete,
  defaultSourceText = '',
}) {
  const [sourceText, setSourceText] = useState(defaultSourceText)
  const [targetLanguage, setTargetLanguage] = useState('hi')
  const [translatedText, setTranslatedText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)
  const [inferenceTime, setInferenceTime] = useState(null)
  const [activeWordCategory, setActiveWordCategory] = useState('verbs')

  const [isSpeaking, setIsSpeaking] = useState(false)
  const [voices, setVoices] = useState([])

  // Preload speech synthesis voices on mount
  useEffect(() => {
    if (!window.speechSynthesis) return

    const loadVoices = () => {
      const available = window.speechSynthesis.getVoices()
      if (available.length > 0) {
        setVoices(available)
      }
    }

    loadVoices()
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices)
    return () => {
      window.speechSynthesis.removeEventListener('voiceschanged', loadVoices)
    }
  }, [])

  // Robust Text-to-Speech with voice selection
  const speakText = (text, lang) => {
    if (!window.speechSynthesis || !text || !text.trim()) return

    // Stop any current speech
    window.speechSynthesis.cancel()

    const utterance = new SpeechSynthesisUtterance(text.trim())

    // Map language codes to BCP-47 locale tags
    const langMap = {
      hi: ['hi-IN', 'hi'],
      mr: ['mr-IN', 'mr', 'hi-IN', 'hi'], // Fallback to Hindi (same Devanagari script) if Marathi voice is missing
      en: ['en-US', 'en-IN', 'en-GB', 'en'],
    }
    const targetTags = langMap[lang] || langMap['en']
    utterance.lang = targetTags[0]

    // Find best matching voice from preloaded list
    const currentVoices = voices.length > 0 ? voices : window.speechSynthesis.getVoices()
    if (currentVoices.length > 0) {
      let bestVoice = null
      for (const tag of targetTags) {
        bestVoice = currentVoices.find(
          (v) => v.lang.toLowerCase().startsWith(tag.toLowerCase())
        )
        if (bestVoice) break
      }
      if (bestVoice) {
        utterance.voice = bestVoice
        utterance.lang = bestVoice.lang
      }
    }

    utterance.rate = 0.9
    utterance.pitch = 1.0
    utterance.volume = 1.0

    utterance.onstart = () => setIsSpeaking(true)
    utterance.onend = () => setIsSpeaking(false)
    utterance.onerror = () => setIsSpeaking(false)

    window.speechSynthesis.speak(utterance)
  }

  // React to prop updates if user clicked from history or dataset explorer
  useEffect(() => {
    if (defaultSourceText) {
      setSourceText(defaultSourceText)
    }
  }, [defaultSourceText])

  const handleTranslate = async () => {
    const textToTranslate = sourceText.trim()
    if (!textToTranslate) {
      setError('Please enter some English text to translate.')
      return
    }

    setIsLoading(true)
    setError('')
    setTranslatedText('')
    setInferenceTime(null)

    try {
      const response = await fetch('http://127.0.0.1:8000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: textToTranslate,
          source_language: 'en',
          target_language: targetLanguage,
        }),
      })

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}))
        throw new Error(errData.detail || `Server returned error ${response.status}`)
      }

      const data = await response.json()
      setTranslatedText(data.translated_text)
      setInferenceTime(data.inference_time_ms)

      if (onTranslationComplete) {
        onTranslationComplete({
          id: Date.now(),
          sourceText: data.source_text,
          translatedText: data.translated_text,
          targetLanguage: data.target_language,
          inferenceTime: data.inference_time_ms,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        })
      }
    } catch (err) {
      console.error('Translation error:', err)
      setError(
        err.message || 'Unable to connect to the translation backend. Ensure FastAPI is running on port 8000.'
      )
    } finally {
      setIsLoading(false)
    }
  }

  const handleClear = () => {
    setSourceText('')
    setTranslatedText('')
    setError('')
    setInferenceTime(null)
  }

  const handleCopy = () => {
    if (!translatedText) return
    navigator.clipboard.writeText(translatedText)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleKeyDown = (e) => {
    // Ctrl+Enter or Cmd+Enter to translate
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleTranslate()
    }
  }

  const handlePickWord = (word) => {
    setSourceText(word)
    setTranslatedText('')
    setInferenceTime(null)
    setError('')
  }

  return (
    <div>
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">English → Regional Language Translator</h1>
        <p className="page-subtitle">
          Real-time Machine Translation into Hindi and Marathi powered by Helsinki-NLP MarianMT Transformer models.
        </p>
      </div>

      {/* Main Translation Card */}
      <div className="glass-card">
        {/* Top Controls Bar */}
        <div className="controls-bar">
          <LanguageSelector
            targetLanguage={targetLanguage}
            setTargetLanguage={setTargetLanguage}
          />

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <button
              className="btn-secondary"
              onClick={handleClear}
              disabled={isLoading || (!sourceText && !translatedText)}
              title="Clear all text"
            >
              <Trash2 size={14} />
              <span>Clear</span>
            </button>

            <button
              className="btn-primary"
              onClick={() => handleTranslate()}
              disabled={isLoading || !sourceText.trim()}
              title="Translate (Ctrl+Enter)"
            >
              {isLoading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  <span>Translating...</span>
                </>
              ) : (
                <>
                  <Send size={16} />
                  <span>Translate</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Quick Words & Examples */}
        <div className="word-bank-container">
          <div className="word-bank-header">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#cbd5e1', fontSize: '0.85rem', fontWeight: 600 }}>
              <BookOpen size={15} color="#818cf8" />
              <span>Quick Try Words & Examples:</span>
            </div>

            <div className="word-category-tabs">
              {Object.entries(WORD_BANK_CATEGORIES).map(([key, category]) => (
                <button
                  key={key}
                  className={`category-tab-btn ${activeWordCategory === key ? 'active' : ''}`}
                  onClick={() => setActiveWordCategory(key)}
                >
                  {category.label}
                </button>
              ))}
            </div>
          </div>

          <div className="word-chips-grid">
            {WORD_BANK_CATEGORIES[activeWordCategory].words.map((w, idx) => (
              <button
                key={idx}
                className="word-chip-btn"
                title={`Click to test translation for: ${w}`}
                onClick={() => handlePickWord(w)}
              >
                <span>{w}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="error-banner">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        {/* Dual Translation Panels */}
        <div className="translation-grid">
          {/* Left Panel: English Input */}
          <div className="panel panel-left">
            <div className="panel-header">
              <span className="panel-title">English Input</span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {sourceText && (
                  <button
                    className={`action-icon-btn ${isSpeaking ? 'speaking' : ''}`}
                    title="Listen to English pronunciation"
                    onClick={() => speakText(sourceText, 'en')}
                  >
                    <Volume2 size={15} />
                  </button>
                )}
                <span className="char-counter">{sourceText.length} / 5000 chars</span>
              </div>
            </div>

            <textarea
              className="translation-textarea"
              placeholder="Type or paste English sentence or paragraph here... (Press Ctrl+Enter to translate)"
              value={sourceText}
              onChange={(e) => {
                setSourceText(e.target.value)
                if (error) setError('')
              }}
              onKeyDown={handleKeyDown}
              maxLength={5000}
            />

            <div className="panel-footer">
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                Tip: Press <kbd style={{ background: '#1e293b', padding: '2px 6px', borderRadius: 4 }}>Ctrl</kbd> + <kbd style={{ background: '#1e293b', padding: '2px 6px', borderRadius: 4 }}>Enter</kbd> to translate
              </span>
            </div>
          </div>

          {/* Right Panel: Translated Output */}
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title">
                {targetLanguage === 'hi' ? 'Hindi Translation (हिन्दी)' : 'Marathi Translation (मराठी)'}
              </span>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {inferenceTime !== null && (
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem',
                      fontSize: '0.75rem',
                      color: '#10b981',
                      background: 'rgba(16, 185, 129, 0.1)',
                      padding: '0.2rem 0.5rem',
                      borderRadius: 4,
                    }}
                  >
                    <Clock size={12} />
                    <span>{inferenceTime} ms</span>
                  </span>
                )}

                {translatedText && (
                  <button
                    className={`action-icon-btn ${isSpeaking ? 'speaking' : ''}`}
                    title="Listen to regional pronunciation"
                    onClick={() => speakText(translatedText, targetLanguage)}
                  >
                    <Volume2 size={15} />
                  </button>
                )}

                {translatedText && (
                  <button
                    className="btn-secondary"
                    onClick={handleCopy}
                    title="Copy translated text"
                  >
                    {copied ? (
                      <>
                        <Check size={14} color="#10b981" />
                        <span style={{ color: '#10b981' }}>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy size={14} />
                        <span>Copy</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>

            <div className="result-area font-devanagari">
              {isLoading ? (
                <div className="result-placeholder">
                  <Loader2 size={32} className="animate-spin" color="#6366f1" />
                  <p>Processing tokens through Transformer model...</p>
                </div>
              ) : translatedText ? (
                <div>{translatedText}</div>
              ) : (
                <div className="result-placeholder">
                  <Sparkles size={32} color="#475569" />
                  <p>Regional translation will appear here after inference</p>
                </div>
              )}
            </div>

            <div className="panel-footer">
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                Model: <code>Helsinki-NLP/opus-mt-en-{targetLanguage}</code>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
