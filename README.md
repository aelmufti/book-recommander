# 📚 AI Book Recommender

An intelligent book recommendation system powered by **Ollama**, **LanceDB**, and **FastAPI**. Describe your reading mood with a few words, and get personalized book recommendations using semantic search and LLM reasoning.

## 🌟 Features

- **Semantic Search**: Uses vector embeddings to find books matching your description
- **LLM-Powered**: Ollama's Llama3 model provides intelligent recommendations
- **Fast Vector DB**: LanceDB for lightning-fast similarity search
- **Beautiful UI**: Modern React frontend with custom gradient theme
- **Simple API**: Clean FastAPI backend with two endpoints

## 🏗️ Architecture

```
User Input → FastAPI → LanceDB (Vector Search) → Ollama (LLM) → Book Recommendation
```

1. User describes their reading preferences with keywords
2. Backend embeds the query using `nomic-embed-text`
3. LanceDB finds top 5 similar books via vector search
4. Llama3 analyzes candidates and picks the best match
5. Returns: Book Title and Author Name

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+**
- **Node.js 18+** and npm
- **Ollama** installed and running

## 🚀 Setup Guide

### Step 1: Install Ollama

#### macOS
```bash
brew install ollama
```

#### Linux
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### Windows
Download from [ollama.com](https://ollama.com)

### Step 2: Pull Required Models

```bash
# Pull the embedding model (for vector search)
ollama pull nomic-embed-text

# Pull the LLM model (for recommendations)
ollama pull llama3
```

### Step 3: Start Ollama Server

```bash
ollama serve
```

Keep this running in a separate terminal. It will run on **http://localhost:11434**

### Step 4: Setup Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize the database (first time only)
python init_database.py

# Start the FastAPI server
uvicorn main:app --reload
```

Backend will run on **http://localhost:8000**

### Step 5: Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will run on **http://localhost:3000**

## 🎯 Usage

1. Open **http://localhost:3000** in your browser
2. Type descriptive words (e.g., "mystery", "adventure", "historical")
3. Press **space** after each word to add it as a tag
4. Click **"Find Book"**
5. Get your personalized recommendation with title and author!

## 📁 Project Structure

```
.
├── main.py                    # FastAPI backend
├── llm_controls.py           # LLM and vector search logic
├── init_database.py          # Database initialization script
├── BooksDatasetClean.csv     # Book dataset
├── requirements.txt          # Python dependencies
├── book_vectors.lancedb/     # LanceDB vector database
└── frontend/                 # React frontend
    ├── src/
    │   ├── App.jsx          # Main React component
    │   ├── main.jsx         # React entry point
    │   └── index.css        # Tailwind + custom styles
    ├── package.json
    ├── tailwind.config.js
    └── vite.config.js
```

## 🔌 API Endpoints

### POST `/recommend`
Get a book recommendation based on your description.

**Request:**
```json
{
  "prompt": "mystery adventure historical",
  "model": "llama3"
}
```

**Response:**
```json
{
  "recommendation": "The Da Vinci Code - Dan Brown"
}
```

### POST `/generate`
Raw LLM generation endpoint.

**Request:**
```json
{
  "prompt": "Tell me about mystery novels",
  "model": "llama3"
}
```

### GET `/`
API information and available endpoints.

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Ollama**: Local LLM inference
- **LanceDB**: Vector database for embeddings
- **Pandas**: Data manipulation

### Frontend
- **React 18**: UI library
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Inter & JetBrains Mono**: Typography

## 📊 Dataset

The book dataset includes:
- **Title**: Book title
- **Authors**: Book authors
- **Description**: Book description
- **Category**: Book category/genre
- **Publisher**: Publishing house
- **Price**: Book price
- **Publish Date**: Publication date (month and year)

## 🎨 Customization

### Add More Books

Edit `BooksDatasetClean.csv` and run:
```bash
python init_database.py
```

### Change LLM Model

In `llm_controls.py`, replace `llama3` with any Ollama model:
```python
ollama.chat(model="mistral", ...)
```

### Modify Prompt

Edit the `system_prompt` in `llm_controls.py` to change recommendation style.

## 🐛 Troubleshooting

### Ollama Connection Error
- Ensure Ollama is running: `ollama serve`
- Check if models are pulled: `ollama list`

### Database Not Found
- Run initialization: `python init_database.py`

### Frontend Can't Connect to Backend
- Verify backend is running on port 8000
- Check proxy settings in `frontend/vite.config.js`

### Port Already in Use
```bash
# Backend (change port)
uvicorn main:app --reload --port 8001

# Frontend (change in vite.config.js)
```

### Large CSV File
If the CSV file is too large, the initialization might take time. The script shows progress every 10 books embedded.

## 📝 License

MIT

## 🤝 Contributing

Feel free to open issues or submit pull requests!

---

**Built with ❤️ using Ollama, LanceDB, and React**