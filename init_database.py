from lancedb import connect
import ollama
import pandas as pd
import time
import pickle
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def embed(text: str, max_retries=2, max_length=2000):
    """Embed text with retry logic and aggressive length limiting"""
    if len(text) > max_length:
        text = text[:max_length]
    
    for attempt in range(max_retries):
        try:
            response = ollama.embed(model="nomic-embed-text", input=text)
            return response["embeddings"][0]
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
            else:
                return None

def build_description(row, max_desc_length=1500):
    """Build searchable description with strict length limits"""
    parts = []
    if pd.notna(row.get("Title")):
        parts.append(f"Title: {row['Title']}")
    if pd.notna(row.get("Authors")):
        parts.append(f"Authors: {row['Authors']}")
    if pd.notna(row.get("Description")):
        desc = str(row["Description"])
        if len(desc) > max_desc_length:
            desc = desc[:max_desc_length]
        parts.append(desc)
    if pd.notna(row.get("Category")):
        parts.append(f"Category: {row['Category']}")
    if pd.notna(row.get("Publisher")):
        parts.append(f"Publisher: {row['Publisher']}")
    return " | ".join(parts)

def save_checkpoint(data, checkpoint_file="checkpoint.pkl"):
    """Save progress to resume later"""
    with open(checkpoint_file, "wb") as f:
        pickle.dump(data, f)

def load_checkpoint(checkpoint_file="checkpoint.pkl"):
    """Load previous progress"""
    if Path(checkpoint_file).exists():
        with open(checkpoint_file, "rb") as f:
            data = pickle.load(f)
        
        # Convert old format to new format
        if "vectors" in data and "indices" in data:
            print(f"  📂 Converting old checkpoint format...")
            results = list(zip(data["indices"], data["vectors"]))
            converted_data = {
                "results": results,
                "last_index": data["last_index"],
                "skipped": data.get("skipped", [])
            }
            print(f"  ✅ Converted {len(results)} embeddings from checkpoint")
            print(f"  📂 Resuming from index {converted_data['last_index']}")
            return converted_data
        
        print(f"  📂 Resuming from index {data['last_index']}")
        return data
    return {"results": [], "last_index": 0, "skipped": []}

def test_ollama_connection():
    """Test if Ollama is working properly"""
    print("Testing Ollama connection...")
    try:
        result = ollama.embed(model="nomic-embed-text", input="test")
        print("  ✅ Ollama connection successful")
        return True
    except Exception as e:
        print(f"  ❌ Ollama connection failed: {e}")
        return False

def process_batch(batch_data):
    """Process a batch of books"""
    results = []
    for idx, text in batch_data:
        vector = embed(text)
        results.append((idx, vector))
    return results

# Configuration
CHECKPOINT_FILE = "embedding_checkpoint.pkl"
CHECKPOINT_INTERVAL = 100
NUM_WORKERS = 8  # Parallel threads - adjust based on your CPU
BATCH_SIZE = 50  # Process in batches

# Test connection first
if not test_ollama_connection():
    print("\n❌ Please restart Ollama and try again")
    exit(1)

print("\nLoading CSV...")
df = pd.read_csv("BooksDatasetClean.csv")

print("Building descriptions...")
df["description"] = df.apply(build_description, axis=1)

desc_lengths = df["description"].str.len()
print(f"Description stats: min={desc_lengths.min()}, max={desc_lengths.max()}, avg={desc_lengths.mean():.0f}")

print("\nConnecting to database...")
db = connect("./book_vectors.lancedb")

# Load checkpoint if exists
checkpoint = load_checkpoint(CHECKPOINT_FILE)
results = checkpoint["results"]
start_index = checkpoint["last_index"]
skipped = checkpoint["skipped"]

if skipped:
    print(f"  ⚠️  Previously skipped {len(skipped)} problematic books")

print(f"\n🚀 Processing {len(df)} books with {NUM_WORKERS} parallel workers...")
print(f"Starting from index {start_index}\n")

start_time = time.time()
successful = len([r for r in results if r[1] is not None])
failed = len(skipped)

# Thread-safe counter for progress
progress_lock = threading.Lock()
processed = start_index

try:
    with ThreadPoolExecutor(max_workers=NUM_WORKERS) as executor:
        # Submit work in batches
        futures = []
        
        for batch_start in range(start_index, len(df), BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE, len(df))
            batch_data = [
                (i, df.iloc[i]["description"]) 
                for i in range(batch_start, batch_end)
            ]
            future = executor.submit(process_batch, batch_data)
            futures.append((batch_start, future))
        
        # Collect results as they complete
        for batch_start, future in futures:
            try:
                batch_results = future.result(timeout=300)  # 5 min timeout per batch
                
                with progress_lock:
                    for idx, vector in batch_results:
                        if vector is None:
                            skipped.append(idx)
                            failed += 1
                        else:
                            results.append((idx, vector))
                            successful += 1
                        
                        processed += 1
                    
                    # Progress update - print every 50 books
                    if processed % 50 == 0 or processed == batch_end:
                        elapsed = time.time() - start_time
                        rate = (processed - start_index) / elapsed if elapsed > 0 else 0
                        remaining = len(df) - processed
                        eta_minutes = (remaining / rate / 60) if rate > 0 else 0
                        
                        print(f"  Progress: {processed}/{len(df)} | "
                              f"✅ {successful} | ⚠️ {failed} | "
                              f"Rate: {rate:.1f}/s | ETA: {eta_minutes:.1f}m")
                    
                    # Save checkpoint
                    if processed % CHECKPOINT_INTERVAL == 0:
                        checkpoint_data = {
                            "results": results,
                            "last_index": processed,
                            "skipped": skipped
                        }
                        save_checkpoint(checkpoint_data, CHECKPOINT_FILE)
                        
            except Exception as e:
                print(f"  ❌ Batch starting at {batch_start} failed: {e}")

except KeyboardInterrupt:
    print("\n⚠️  Interrupted by user")
    checkpoint_data = {
        "results": results,
        "last_index": processed,
        "skipped": skipped
    }
    save_checkpoint(checkpoint_data, CHECKPOINT_FILE)
    print("Progress saved. Run script again to resume.")
    exit(1)

# Sort results by index and create dataframe
print("\nBuilding final dataset...")
results.sort(key=lambda x: x[0])
indices = [r[0] for r in results]
vectors = [r[1] for r in results]

successful_df = df.iloc[indices].copy()
successful_df = successful_df[["Title", "Authors", "description"]].copy()
successful_df.columns = ["title", "authors", "description"]
successful_df["vector"] = vectors

print("Creating database table...")
db.create_table("books", data=successful_df, mode="overwrite")

if Path(CHECKPOINT_FILE).exists():
    Path(CHECKPOINT_FILE).unlink()

elapsed_total = time.time() - start_time
print(f"\n✅ Database initialized successfully!")
print(f"   📚 Total books processed: {len(df)}")
print(f"   ✅ Successfully embedded: {len(vectors)}")
print(f"   ⚠️  Skipped (problematic): {len(skipped)}")
print(f"   ⏱️  Total time: {elapsed_total/60:.1f} minutes")
print(f"   🚀 Average rate: {len(vectors)/elapsed_total:.1f} books/second")

if skipped:
    print(f"\n📝 Skipped book indices: {skipped[:10]}{'...' if len(skipped) > 10 else ''}")