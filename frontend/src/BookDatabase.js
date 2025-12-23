// Configuration de l'API
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000'

// Base de données de livres de fallback (si l'API n'est pas disponible)
export const DEMO_BOOKS = [
  {
    title: "Le Petit Prince",
    authors: "Antoine de Saint-Exupéry", 
    genres: "Fiction, Jeunesse",
    keywords: "prince planète rose renard amitié voyage",
    avg_rating: 4.5,
    ratings_count: 50000,
    popularity_tier: "popular",
    language: "fre",
    first_publish_date: 1943
  },
  {
    title: "Harry Potter à l'école des sorciers",
    authors: "J.K. Rowling",
    genres: "Fantasy, Jeunesse", 
    keywords: "magie sorcier école amitié poudlard",
    avg_rating: 4.7,
    ratings_count: 120000,
    popularity_tier: "popular",
    language: "fre",
    first_publish_date: 1997
  },
  {
    title: "1984",
    authors: "George Orwell",
    genres: "Science Fiction, Dystopie",
    keywords: "surveillance totalitarisme liberté big brother",
    avg_rating: 4.2,
    ratings_count: 80000,
    popularity_tier: "popular", 
    language: "eng",
    first_publish_date: 1949
  },
  {
    title: "L'Étranger",
    authors: "Albert Camus",
    genres: "Fiction, Philosophie",
    keywords: "absurde étranger société existentialisme",
    avg_rating: 4.1,
    ratings_count: 30000,
    popularity_tier: "known",
    language: "fre",
    first_publish_date: 1942
  },
  {
    title: "Dune",
    authors: "Frank Herbert",
    genres: "Science Fiction",
    keywords: "épice désert politique prophétie arrakis",
    avg_rating: 4.6,
    ratings_count: 45000,
    popularity_tier: "popular",
    language: "eng",
    first_publish_date: 1965
  },
  {
    title: "Le Seigneur des anneaux",
    authors: "J.R.R. Tolkien",
    genres: "Fantasy, Épique",
    keywords: "anneau hobbit aventure magie terre milieu",
    avg_rating: 4.8,
    ratings_count: 150000,
    popularity_tier: "popular",
    language: "eng",
    first_publish_date: 1954
  },
  {
    title: "Les Misérables",
    authors: "Victor Hugo",
    genres: "Fiction, Historique",
    keywords: "révolution paris jean valjean justice",
    avg_rating: 4.4,
    ratings_count: 25000,
    popularity_tier: "known",
    language: "fre",
    first_publish_date: 1862
  },
  {
    title: "Madame Bovary",
    authors: "Gustave Flaubert",
    genres: "Fiction, Classique",
    keywords: "femme mariage ennui province réalisme",
    avg_rating: 3.9,
    ratings_count: 18000,
    popularity_tier: "known",
    language: "fre",
    first_publish_date: 1857
  },
  {
    title: "Cent ans de solitude",
    authors: "Gabriel García Márquez",
    genres: "Réalisme magique",
    keywords: "famille solitude amérique latine magie",
    avg_rating: 4.3,
    ratings_count: 35000,
    popularity_tier: "known",
    language: "spa",
    first_publish_date: 1967
  },
  {
    title: "Don Quichotte",
    authors: "Miguel de Cervantes",
    genres: "Fiction, Classique",
    keywords: "chevalier aventure espagne rêve",
    avg_rating: 4.0,
    ratings_count: 20000,
    popularity_tier: "known",
    language: "spa",
    first_publish_date: 1605
  },
  {
    title: "Der Zauberberg",
    authors: "Thomas Mann",
    genres: "Fiction, Philosophie",
    keywords: "montagne sanatorium temps allemagne",
    avg_rating: 4.2,
    ratings_count: 15000,
    popularity_tier: "known",
    language: "ger",
    first_publish_date: 1924
  },
  {
    title: "Pride and Prejudice",
    authors: "Jane Austen",
    genres: "Romance, Classique",
    keywords: "amour société mariage angleterre",
    avg_rating: 4.3,
    ratings_count: 85000,
    popularity_tier: "popular",
    language: "eng",
    first_publish_date: 1813
  },
  {
    title: "To Kill a Mockingbird",
    authors: "Harper Lee",
    genres: "Fiction, Drame",
    keywords: "justice racisme enfance amérique sud",
    avg_rating: 4.4,
    ratings_count: 95000,
    popularity_tier: "popular",
    language: "eng",
    first_publish_date: 1960
  },
  {
    title: "Le Rouge et le Noir",
    authors: "Stendhal",
    genres: "Fiction, Classique",
    keywords: "ambition amour société napoléon",
    avg_rating: 4.0,
    ratings_count: 22000,
    popularity_tier: "known",
    language: "fre",
    first_publish_date: 1830
  },
  {
    title: "Germinal",
    authors: "Émile Zola",
    genres: "Fiction, Réalisme",
    keywords: "mine ouvriers grève révolution sociale",
    avg_rating: 4.1,
    ratings_count: 19000,
    popularity_tier: "known",
    language: "fre",
    first_publish_date: 1885
  }
]

// Fonction pour rechercher via l'API
export async function searchBooks(prompt, language = 'fre') {
  if (!prompt) return []
  
  try {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: prompt,
        language: language,
        use_llm: false
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    
    // Retourner les candidats de l'API
    return data.all_candidates || []
    
  } catch (error) {
    console.warn('API non disponible, utilisation des données locales:', error)
    
    // Fallback vers la recherche locale
    return searchBooksLocal(prompt, language)
  }
}

// Fonction pour obtenir un livre aléatoire via l'API
export async function getRandomUnknownBook(language = 'fre') {
  try {
    const response = await fetch(`${API_BASE_URL}/random-unknown?language=${language}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    return data.book
    
  } catch (error) {
    console.warn('API non disponible pour livre aléatoire:', error)
    
    // Fallback vers les données locales
    const filteredBooks = DEMO_BOOKS.filter(book => 
      language === 'all' || book.language === language
    )
    
    const unknownBooks = filteredBooks.filter(book => 
      book.popularity_tier === 'known' || book.ratings_count < 50000
    )
    
    const booksToChooseFrom = unknownBooks.length > 0 ? unknownBooks : filteredBooks
    
    if (booksToChooseFrom.length > 0) {
      return booksToChooseFrom[Math.floor(Math.random() * booksToChooseFrom.length)]
    }
    
    return null
  }
}

// Fonction de recherche locale (fallback)
function searchBooksLocal(prompt, language = 'all') {
  if (!prompt) return []
  
  const keywords = prompt.toLowerCase().split(' ').filter(k => k.length > 2)
  const results = []
  
  for (const book of DEMO_BOOKS) {
    // Filtrer par langue
    if (language && language !== 'all') {
      if (language.includes(',')) {
        const langs = language.split(',').map(l => l.trim())
        if (!langs.includes(book.language)) continue
      } else if (book.language !== language) {
        continue
      }
    }
    
    // Calculer le score de correspondance
    let score = 0
    const searchText = `${book.title} ${book.authors} ${book.keywords} ${book.genres}`.toLowerCase()
    
    for (const keyword of keywords) {
      if (searchText.includes(keyword)) {
        // Bonus pour les correspondances dans le titre
        if (book.title.toLowerCase().includes(keyword)) {
          score += 5
        }
        // Bonus pour les correspondances dans l'auteur
        else if (book.authors.toLowerCase().includes(keyword)) {
          score += 3
        }
        // Bonus pour les mots-clés
        else if (book.keywords.toLowerCase().includes(keyword)) {
          score += 2
        }
        // Score normal pour les autres correspondances
        else {
          score += 1
        }
      }
    }
    
    if (score > 0) {
      results.push({ book, score })
    }
  }
  
  // Trier par score puis par popularité
  results.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score
    return b.book.ratings_count - a.book.ratings_count
  })
  
  return results.map(r => r.book)
}