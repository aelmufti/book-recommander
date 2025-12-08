import { useState } from 'react'

function App() {
  const [words, setWords] = useState([])
  const [currentInput, setCurrentInput] = useState('')
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)

  const handleKeyDown = (e) => {
    if (e.key === ' ' && currentInput.trim()) {
      e.preventDefault()
      setWords([...words, currentInput.trim()])
      setCurrentInput('')
    }
  }

  const handleSearch = async () => {
    if (words.length === 0) return

    setLoading(true)
    setRecommendation(null)

    try {
      const prompt = words.join(' ')
      const response = await fetch('/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt })
      })

      const data = await response.json()
      
      // Parse the response to extract title and author
      const text = data.recommendation
      const match = text.match(/(.+?)\s*-\s*(.+)/)
      
      if (match) {
        setRecommendation({
          title: match[1].trim(),
          author: match[2].trim(),
          raw: text
        })
      } else {
        setRecommendation({
          title: 'Book Found',
          author: '',
          raw: text
        })
      }
    } catch (error) {
      setRecommendation({
        title: 'Error',
        author: '',
        raw: error.message
      })
    } finally {
      setLoading(false)
    }
  }

  const removeWord = (index) => {
    setWords(words.filter((_, i) => i !== index))
  }

  const clearAll = () => {
    setWords([])
    setCurrentInput('')
    setRecommendation(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-[hsl(30,45%,12%)] via-[hsl(35,40%,18%)] to-[hsl(40,35%,22%)] flex items-center justify-center p-4 sm:p-8">
      <div className="w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8 animate-fade-in">
          <h1 className="text-5xl sm:text-6xl font-bold mb-3 gradient-text">
            📚 Book Finder
          </h1>
          <p className="text-muted-foreground text-lg font-mono">
            Describe your reading mood, discover your next book
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-card rounded-lg shadow-card-hover p-6 sm:p-8 animate-slide-up">
          {/* Input Section */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-muted-foreground mb-2 font-mono">
              Type words and press space
            </label>
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="mystery adventure historical..."
              className="w-full px-4 py-3 bg-secondary border-2 border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all font-mono text-foreground placeholder:text-muted-foreground"
            />
          </div>

          {/* Words Display */}
          <div className="min-h-[80px] mb-6 p-4 bg-secondary/50 rounded-lg border-2 border-border">
            {words.length === 0 ? (
              <p className="text-muted-foreground text-center py-4 font-mono text-sm">
                Your words will appear here...
              </p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {words.map((word, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-full font-medium text-sm shadow-md hover:shadow-lg transition-all animate-fade-in"
                  >
                    {word}
                    <button
                      onClick={() => removeWord(index)}
                      className="hover:bg-white/20 rounded-full w-5 h-5 flex items-center justify-center transition-colors"
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Buttons */}
          <div className="flex gap-3 mb-6">
            <button
              onClick={handleSearch}
              disabled={words.length === 0 || loading}
              className="flex-1 px-6 py-3 bg-gradient-to-r from-primary to-accent text-primary-foreground rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-glow transition-all duration-300 font-mono"
            >
              {loading ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Searching...
                </span>
              ) : (
                'Find Book'
              )}
            </button>
            <button
              onClick={clearAll}
              className="px-6 py-3 bg-secondary text-secondary-foreground rounded-lg font-semibold hover:bg-secondary/80 transition-all font-mono"
            >
              Clear
            </button>
          </div>

          {/* Recommendation Display */}
          {recommendation && (
            <div className="p-6 bg-gradient-to-br from-primary/10 to-accent/10 border-2 border-primary/30 rounded-lg animate-slide-up">
              <div className="flex items-start gap-4">
                <div className="text-4xl">📖</div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-foreground mb-2">
                    {recommendation.title}
                  </h2>
                  <div className="flex flex-wrap gap-4 text-muted-foreground font-mono">
                    {recommendation.author && (
                      <div className="flex items-center gap-2">
                        <span className="text-primary">✍️</span>
                        <span>{recommendation.author}</span>
                      </div>
                    )}
                  </div>
                  {!recommendation.author && (
                    <p className="text-muted-foreground mt-2 font-mono text-sm">
                      {recommendation.raw}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-6 text-muted-foreground text-sm font-mono animate-fade-in">
          Powered by Ollama + LanceDB
        </div>
      </div>
    </div>
  )
}

export default App
