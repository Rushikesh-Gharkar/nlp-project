import React from 'react'
import { History, Trash2, Copy, Check, ArrowRight } from 'lucide-react'

export default function TranslationHistory({ history, onClearHistory, onSelectHistoryItem }) {
  const [copiedId, setCopiedId] = React.useState(null)

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  if (!history || history.length === 0) {
    return null
  }

  return (
    <div className="glass-card history-card">
      <div className="history-header">
        <div className="history-title">
          <History size={18} color="#6366f1" />
          <span>Translation History</span>
          <span style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: 500 }}>
            ({history.length} {history.length === 1 ? 'item' : 'items'})
          </span>
        </div>

        <button className="btn-secondary" onClick={onClearHistory} title="Clear history">
          <Trash2 size={14} />
          <span>Clear History</span>
        </button>
      </div>

      <div className="history-list">
        {history.map((item) => (
          <div key={item.id} className="history-item">
            <div className="history-item-header">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="history-lang-badge">
                  EN → {item.targetLanguage === 'hi' ? 'Hindi (हिन्दी)' : 'Marathi (मराठी)'}
                </span>
                {item.inferenceTime && (
                  <span style={{ fontSize: '0.75rem', color: '#64748b' }}>
                    {item.inferenceTime} ms
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="history-time">{item.timestamp}</span>
                <button
                  className="btn-secondary"
                  style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}
                  onClick={() => handleCopy(item.id, item.translatedText)}
                  title="Copy translation"
                >
                  {copiedId === item.id ? (
                    <Check size={12} color="#10b981" />
                  ) : (
                    <Copy size={12} />
                  )}
                </button>
              </div>
            </div>

            <div
              className="history-source"
              style={{ cursor: 'pointer' }}
              onClick={() => onSelectHistoryItem && onSelectHistoryItem(item)}
              title="Click to load into editor"
            >
              <strong style={{ color: '#94a3b8' }}>English: </strong>
              <span>{item.sourceText}</span>
            </div>

            <div className="history-target font-devanagari">
              <strong style={{ color: '#a5b4fc', fontSize: '0.9rem' }}>
                {item.targetLanguage === 'hi' ? 'Hindi: ' : 'Marathi: '}
              </strong>
              <span>{item.translatedText}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
