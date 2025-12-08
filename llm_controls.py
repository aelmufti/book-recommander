from lancedb import connect
import ollama

def embed(text: str):
    response = ollama.embed(model="nomic-embed-text", input=text)
    return response["embeddings"][0]

def get_table():
    db = connect("./book_vectors.lancedb")
    return db.open_table("books")

def recommend_book(prompt: str) -> str:
    """Semantic search + LLM reasoning → final book recommendation."""
    
    tbl = get_table()
    query_vec = embed(prompt)
    matches = tbl.search(query_vec).limit(5).to_pandas()

    system_prompt = """
You are a book recommendation expert.
From the candidate books, choose *one* best book that matches the user's prompt.
Answer format (STRICT):
Book Title - Author Name

Example: The Great Gatsby - F. Scott Fitzgerald

Only provide the book title and author name. Nothing else.
"""

    response = ollama.chat(
        model="llama3",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"User wants: {prompt}\n\nHere are candidate books:\n{matches}"
            }
        ]
    )

    return response["message"]["content"]
