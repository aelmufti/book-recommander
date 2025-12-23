import { useState, useRef } from 'react'

function GlassCard({ children, className = '' }) {
  return (
    <div className={`glass-card ${className}`}>
      <div className="glass-filter"></div>
      <div className="glass-overlay"></div>
      <div className="glass-specular"></div>
      <div className="glass-content">
        {children}
      </div>
    </div>
  )
}

function App() {
  const [inputValue, setInputValue] = useState('')
  const [keywords, setKeywords] = useState([])
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  
  // Unknown section state
  const [unknownBook, setUnknownBook] = useState(null)
  const [unknownLoading, setUnknownLoading] = useState(false)
  const [unknownLang, setUnknownLang] = useState('all')
  const unknownSectionRef = useRef(null)

  const languages = {
    'fre': { flag: '🇫🇷', name: 'Français' },
    'eng': { flag: '🇬🇧', name: 'English' },
    'spa': { flag: '🇪🇸', name: 'Español' },
    'ger': { flag: '🇩🇪', name: 'Deutsch' },
    'ita': { flag: '🇮🇹', name: 'Italiano' },
    'por': { flag: '🇵🇹', name: 'Português' },
  }

  // Detect browser language and map to our language codes
  const getBrowserLanguage = () => {
    const browserLang = navigator.language || navigator.userLanguage || 'en'
    const langMap = {
      'fr': 'fre', 'en': 'eng', 'es': 'spa', 'de': 'ger', 'it': 'ita', 'pt': 'por'
    }
    const shortLang = browserLang.split('-')[0].toLowerCase()
    return langMap[shortLang] || 'eng'
  }

  const [uiLanguage] = useState(getBrowserLanguage)
  const [selectedLanguages, setSelectedLanguages] = useState(() => [getBrowserLanguage()])

  const toggleLanguage = (code) => {
    if (selectedLanguages.includes(code)) {
      if (selectedLanguages.length > 1) {
        setSelectedLanguages(selectedLanguages.filter(l => l !== code))
      }
    } else {
      setSelectedLanguages([...selectedLanguages, code])
    }
  }

  const selectAllLanguages = () => {
    if (selectedLanguages.length === Object.keys(languages).length) {
      setSelectedLanguages([uiLanguage])
    } else {
      setSelectedLanguages(Object.keys(languages))
    }
  }

  const translations = {
    'fre': {
      subtitle: '43M+ livres · Recherche IA',
      langLabel: 'Langue des résultats',
      allLangs: 'Toutes les langues',
      keywords: 'Mots-clés (Espace ou Entrée pour ajouter)',
      placeholder: 'roman policier, Agatha Christie, voyage dans le temps...',
      addMore: 'Ajouter...',
      hint: 'mots-clés · 2-3 suffisent généralement',
      search: '🔍 Rechercher',
      searching: 'Recherche...',
      results: 'résultats',
      by: 'par',
      reviews: 'avis',
      noResults: 'Aucun livre trouvé. Essayez d\'autres mots-clés.',
      error: 'Erreur de connexion',
      // Unknown section
      unknownTitle: 'Le Puits de l\'Inconnu',
      unknownSubtitle: 'Plongez dans l\'obscurité littéraire',
      unknownDesc: 'Des millions de livres oubliés attendent d\'être découverts. Aucune note, aucun avis — juste vous et l\'inconnu.',
      unknownBtn: '🎲 Révéler un livre mystère',
      unknownLoading: 'Plongée...',
      unknownLang: 'Langue',
      scrollDown: 'Descendre dans le puits',
      published: 'Publié en'
    },
    'eng': {
      subtitle: '43M+ books · AI-Powered Search',
      langLabel: 'Results language',
      allLangs: 'All languages',
      keywords: 'Keywords (Space or Enter to add)',
      placeholder: 'dystopian fiction, George Orwell, coming of age...',
      addMore: 'Add more...',
      hint: 'keywords · 2-3 usually enough',
      search: '🔍 Search',
      searching: 'Searching...',
      results: 'results',
      by: 'by',
      reviews: 'reviews',
      noResults: 'No books found. Try other keywords.',
      error: 'Connection error',
      // Unknown section
      unknownTitle: 'The Well of Unknown',
      unknownSubtitle: 'Dive into literary darkness',
      unknownDesc: 'Millions of forgotten books waiting to be discovered. No ratings, no reviews — just you and the unknown.',
      unknownBtn: '🎲 Reveal a mystery book',
      unknownLoading: 'Diving...',
      unknownLang: 'Language',
      scrollDown: 'Descend into the well',
      published: 'Published in'
    },
    'spa': {
      subtitle: '43M+ libros · Búsqueda con IA',
      langLabel: 'Idioma de resultados',
      allLangs: 'Todos los idiomas',
      keywords: 'Palabras clave (Espacio o Enter para añadir)',
      placeholder: 'realismo mágico, García Márquez, aventura...',
      addMore: 'Añadir...',
      hint: 'palabras clave · 2-3 suelen bastar',
      search: '🔍 Buscar',
      searching: 'Buscando...',
      results: 'resultados',
      by: 'por',
      reviews: 'reseñas',
      noResults: 'No se encontraron libros. Prueba otras palabras.',
      error: 'Error de conexión',
      // Unknown section
      unknownTitle: 'El Pozo de lo Desconocido',
      unknownSubtitle: 'Sumérgete en la oscuridad literaria',
      unknownDesc: 'Millones de libros olvidados esperan ser descubiertos. Sin notas, sin reseñas — solo tú y lo desconocido.',
      unknownBtn: '🎲 Revelar un libro misterio',
      unknownLoading: 'Sumergiéndose...',
      unknownLang: 'Idioma',
      scrollDown: 'Descender al pozo',
      published: 'Publicado en'
    },
    'ger': {
      subtitle: '43M+ Bücher · KI-gestützte Suche',
      langLabel: 'Ergebnissprache',
      allLangs: 'Alle Sprachen',
      keywords: 'Stichwörter (Leertaste oder Enter zum Hinzufügen)',
      placeholder: 'Krimi, Hermann Hesse, Weltkrieg...',
      addMore: 'Hinzufügen...',
      hint: 'Stichwörter · 2-3 reichen meist',
      search: '🔍 Suchen',
      searching: 'Suche...',
      results: 'Ergebnisse',
      by: 'von',
      reviews: 'Bewertungen',
      noResults: 'Keine Bücher gefunden. Versuche andere Stichwörter.',
      error: 'Verbindungsfehler',
      // Unknown section
      unknownTitle: 'Der Brunnen des Unbekannten',
      unknownSubtitle: 'Tauche in die literarische Dunkelheit',
      unknownDesc: 'Millionen vergessener Bücher warten darauf, entdeckt zu werden. Keine Bewertungen — nur du und das Unbekannte.',
      unknownBtn: '🎲 Ein Geheimbuch enthüllen',
      unknownLoading: 'Tauche...',
      unknownLang: 'Sprache',
      scrollDown: 'In den Brunnen hinabsteigen',
      published: 'Veröffentlicht'
    },
    'ita': {
      subtitle: '43M+ libri · Ricerca con IA',
      langLabel: 'Lingua dei risultati',
      allLangs: 'Tutte le lingue',
      keywords: 'Parole chiave (Spazio o Invio per aggiungere)',
      placeholder: 'giallo, Umberto Eco, rinascimento...',
      addMore: 'Aggiungi...',
      hint: 'parole chiave · 2-3 di solito bastano',
      search: '🔍 Cerca',
      searching: 'Ricerca...',
      results: 'risultati',
      by: 'di',
      reviews: 'recensioni',
      noResults: 'Nessun libro trovato. Prova altre parole chiave.',
      error: 'Errore di connessione',
      // Unknown section
      unknownTitle: 'Il Pozzo dell\'Ignoto',
      unknownSubtitle: 'Immergiti nell\'oscurità letteraria',
      unknownDesc: 'Milioni di libri dimenticati aspettano di essere scoperti. Nessun voto, nessuna recensione — solo tu e l\'ignoto.',
      unknownBtn: '🎲 Rivela un libro misterioso',
      unknownLoading: 'Immersione...',
      unknownLang: 'Lingua',
      scrollDown: 'Scendi nel pozzo',
      published: 'Pubblicato nel'
    },
    'por': {
      subtitle: '43M+ livros · Pesquisa com IA',
      langLabel: 'Idioma dos resultados',
      allLangs: 'Todos os idiomas',
      keywords: 'Palavras-chave (Espaço ou Enter para adicionar)',
      placeholder: 'romance histórico, José Saramago, suspense...',
      addMore: 'Adicionar...',
      hint: 'palavras-chave · 2-3 geralmente bastam',
      search: '🔍 Pesquisar',
      searching: 'Pesquisando...',
      results: 'resultados',
      by: 'por',
      reviews: 'avaliações',
      noResults: 'Nenhum livro encontrado. Tente outras palavras.',
      error: 'Erro de conexão',
      // Unknown section
      unknownTitle: 'O Poço do Desconhecido',
      unknownSubtitle: 'Mergulhe na escuridão literária',
      unknownDesc: 'Milhões de livros esquecidos esperando para serem descobertos. Sem notas, sem avaliações — apenas você e o desconhecido.',
      unknownBtn: '🎲 Revelar um livro misterioso',
      unknownLoading: 'Mergulhando...',
      unknownLang: 'Idioma',
      scrollDown: 'Descer ao poço',
      published: 'Publicado em'
    }
  }

  const t = translations[uiLanguage] || translations['eng']

  const scrollToUnknown = () => {
    unknownSectionRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const fetchUnknownBook = async () => {
    setUnknownLoading(true)
    setUnknownBook(null)
    
    try {
      // Version démo - livre aléatoire depuis la liste
      const demoBooks = [
        {
          title: "Le Petit Prince",
          authors: "Antoine de Saint-Exupéry",
          genres: "Fiction, Jeunesse",
          avg_rating: 4.5,
          ratings_count: 50000,
          popularity_tier: "popular",
          language: "fre",
          first_publish_date: 1943
        },
        {
          title: "L'Étranger", 
          authors: "Albert Camus",
          genres: "Fiction, Philosophie",
          avg_rating: 4.1,
          ratings_count: 30000,
          popularity_tier: "known",
          language: "fre",
          first_publish_date: 1942
        }
      ]
      
      const randomBook = demoBooks[Math.floor(Math.random() * demoBooks.length)]
      setUnknownBook(randomBook)
    } catch {
      setUnknownBook(null)
    } finally {
      setUnknownLoading(false)
    }
  }

  const addKeyword = (e) => {
    if (e.key === 'Enter' || e.key === ' ' || e.key === ',') {
      e.preventDefault()
      const word = inputValue.trim().toLowerCase().replace(/[,\s]/g, '')
      if (word && !keywords.includes(word) && keywords.length < 6) {
        setKeywords([...keywords, word])
        setInputValue('')
      }
    }
    // Backspace on empty input removes last keyword
    if (e.key === 'Backspace' && inputValue === '' && keywords.length > 0) {
      setKeywords(keywords.slice(0, -1))
    }
  }

  const removeKeyword = (index) => {
    setKeywords(keywords.filter((_, i) => i !== index))
  }

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (keywords.length === 0) return
    
    setLoading(true)
    setResults(null)

    try {
      const response = await fetch('/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: keywords.join(' '),
          language: 'all',
          use_llm: true
        })
      })

      const data = await response.json()
      setResults(data)
    } catch {
      setResults({ error: 'Erreur de connexion' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="scene">
        {/* SVG Filter for Glass Distortion */}
        <svg style={{ display: 'none' }}>
          <filter id="glass-distortion">
            <feTurbulence type="turbulence" baseFrequency="0.01" numOctaves="3" result="noise" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="8" />
          </filter>
        </svg>

        {/* Background pattern */}
        <div className="bg-pattern"></div>
        <div className="bg-orbs"></div>
        
        <div className="container">
          {/* Header */}
          <div className="header">
            <div className="header-icon">📚</div>
            <h1 className="header-title">Book Finder</h1>
            <p className="header-sub">{t.subtitle}</p>
          </div>

          {/* Search Form */}
          <GlassCard className="card-search">
            <form onSubmit={handleSearch}>
              <label className="label">{t.keywords}</label>
              
              <div className="keywords-area">
                {keywords.map((kw, i) => (
                  <span key={i} className="keyword-tag">
                    {kw}
                    <button type="button" onClick={() => removeKeyword(i)} className="keyword-remove">×</button>
                  </span>
                ))}
                
                {keywords.length < 6 && (
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={addKeyword}
                    placeholder={keywords.length === 0 ? t.placeholder : t.addMore}
                    className="keyword-input"
                    autoComplete="off"
                  />
                )}
              </div>
              
              <p className="keywords-hint">{keywords.length}/6 {t.hint}</p>

              <button
                type="submit"
                disabled={keywords.length === 0 || loading}
                className="search-btn"
              >
                {loading ? (
                  <span className="btn-loading">
                    <span className="spinner"></span>
                    {t.searching}
                  </span>
                ) : (
                  t.search
                )}
              </button>
            </form>
          </GlassCard>

          {/* Results */}
          {results && !results.error && (
            <div className="results">
              <div className="results-info">
                🔑 {results.keywords_used?.slice(0, 4).join(', ')} · {results.candidates_count} {t.results}
                {results.llm_used && ' · 🤖 AI'}
              </div>

              {results.candidates_count === 0 && (
                <GlassCard>
                  <p className="no-results">{t.noResults}</p>
                </GlassCard>
              )}

              {results.all_candidates?.map((book, i) => (
                <GlassCard key={i} className="card-result">
                  <div className="result-row">
                    <div className="result-icon">{i === 0 ? '🏆' : '📖'}</div>
                    <div className="result-info">
                      <h3 className="result-title">{book.title}</h3>
                      <p className="result-author">{t.by} {book.authors}</p>
                      <div className="result-meta">
                        {book.avg_rating && (
                          <span className="rating">⭐ {book.avg_rating.toFixed(1)}</span>
                        )}
                        {book.ratings_count && (
                          <span className="reviews">({book.ratings_count.toLocaleString()} {t.reviews})</span>
                        )}
                        <span className={`tier ${book.popularity_tier}`}>
                          {book.popularity_tier}
                        </span>
                        <span className="lang-flag">
                          {languages[book.language]?.flag || book.language}
                        </span>
                      </div>
                    </div>
                  </div>
                </GlassCard>
              ))}
            </div>
          )}

          {results?.error && (
            <div className="error-msg">{t.error}</div>
          )}

          {/* Scroll indicator */}
          <div className="scroll-indicator" onClick={scrollToUnknown}>
            <span className="scroll-text">{t.scrollDown}</span>
            <div className="scroll-arrow">
              <span>↓</span>
              <span>↓</span>
              <span>↓</span>
            </div>
          </div>
        </div>
      </div>

      {/* ═══════════════════════════════════════════════════════════
          UNKNOWN SECTION - The Well (separate from scene)
          ═══════════════════════════════════════════════════════════ */}
      <div className="unknown-section" ref={unknownSectionRef}>
        <div className="well-bg"></div>
        <div className="well-particles"></div>
        
        <div className="container">
          <div className="unknown-header">
            <div className="unknown-icon">🕳️</div>
            <h2 className="unknown-title">{t.unknownTitle}</h2>
            <p className="unknown-subtitle">{t.unknownSubtitle}</p>
          </div>

          <GlassCard className="card-unknown">
            <p className="unknown-desc">{t.unknownDesc}</p>
            
            <div className="unknown-lang-select">
              <span className="label">{t.unknownLang}</span>
              <div className="unknown-lang-grid">
                <button
                  onClick={() => setUnknownLang('all')}
                  className={`lang-btn ${unknownLang === 'all' ? 'active' : ''}`}
                >
                  🌍 {t.allLangs}
                </button>
                {Object.entries(languages).map(([code, { flag, name }]) => (
                  <button
                    key={code}
                    onClick={() => setUnknownLang(code)}
                    className={`lang-btn ${unknownLang === code ? 'active' : ''}`}
                  >
                    <span>{flag}</span> {name}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={fetchUnknownBook}
              disabled={unknownLoading}
              className="unknown-btn"
            >
              {unknownLoading ? (
                <span className="btn-loading">
                  <span className="spinner"></span>
                  {t.unknownLoading}
                </span>
              ) : (
                t.unknownBtn
              )}
            </button>
          </GlassCard>

          {unknownBook && (
            <GlassCard className="card-mystery">
              <div className="mystery-reveal">
                <div className="mystery-icon">📜</div>
                <h3 className="mystery-title">{unknownBook.title}</h3>
                <p className="mystery-author">{t.by} {unknownBook.authors}</p>
                {unknownBook.first_publish_date && (
                  <p className="mystery-date">{t.published} {unknownBook.first_publish_date}</p>
                )}
                {unknownBook.genres && (
                  <p className="mystery-genres">{unknownBook.genres}</p>
                )}
                <div className="mystery-meta">
                  <span className="tier unknown">unknown</span>
                  <span className="lang-flag">
                    {languages[unknownBook.language]?.flag || unknownBook.language}
                  </span>
                </div>
              </div>
            </GlassCard>
          )}
        </div>
      </div>
    </>
  )
}

export default App
