import os
import json
import openai
import time
import requests
import pandas as pd
import config

OPENAI_API_KEY = 0 # REPLACE WITH ACTUAL KEY
client = openai.OpenAI(api_key=OPENAI_API_KEY)

GOOGLE_API_KEY = 0 # REPLACE WITH ACTUAL KEY
SEARCH_ENGINE_ID = 0  # REPLACE WITH ACTUAL GOOGLE CUSTOM SEARCH ENGINE ID

def google_search(query):
    """Search Google for book-related metadata and return snippets."""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        snippets = [item["snippet"] for item in data.get("items", [])[:10]]  # Get top snippets
        return " ".join(snippets)  # Merge snippets for context
    else:
        print(f"Google Search Error: {response.status_code}")
        return None  

def generate_book_prompt(book_title, book_author, search_results=None, book_summary=None, book_blurb=None):
    """Generates the prompt for book details, optionally including web search context and book descriptions."""
    
    search_context = f"\n\nHere is additional web search information for context:\n{search_results}" if search_results else ""
    summary_context = f"\n\nA detailed plot summary is:\n{book_summary}" if book_summary else ""
    description_context = f"\n\nThe book promotional blurb is:\n{book_blurb}" if book_blurb else ""

    return f"""
    You are a literary expert with deep knowledge of every best-selling book of the past decades. 
    Use your encyclopedic knowledge of books to retrieve detailed information.{search_context}{summary_context}{description_context}

    **Step 1: Determine the Genre and Main Setting**
    - Identify the **genre** of the book. Provide a **one-word or short-phrase descriptor**.

    **Step 2: Identify Protagonists (Only POV/Main Characters)**
    - List only the **POV characters** or the **main narrators**.
    - If the book features an **ensemble cast**, return **all protagonists**.
    - Ensure that **supporting characters are not included**.

    **Step 3: Assign Correct Professions (No Personality Traits)**
    - Provide the **exact profession(s)** for each protagonist **in the same order**.
    - If a character **changes professions**, list all relevant professions in **chronological order**.
    - Always prefer **specific job titles** over general ones (e.g., "Neurosurgeon" instead of "Doctor").
    - **Strict rule**: Do not return personality-based words or identity markers that are not professions (e.g., "Kindest person" is invalid).
    - If a profession is **completely unknown**, return "Unknown" instead of making assumptions.

    **Step 4: Profession Mapping to ISCO Codes**
    - Convert each profession into the **best ISCO code guess**.
    - Ensure that ISCO codes follow the **same order as professions**.
    - If a profession is unknown, return **0**. If unsure, return **9**.

    **Step 5: Identify Love Interest (If Applicable)**
    - Identify the **main love interest**, if applicable.
    - Provide their **exact profession(s)** using the same rules as above.
    - Convert their profession(s) into **ISCO codes**, following the same logic.

    **Final Output Format (JSON):**
    {{
      "Book Title": "{book_title}",
      "Book Author": "{book_author}",
      "Genre": "<genre>",
      "Protagonists": ["<name1>", "<name2>", ...],
      "Professions": [["<profession1a>", "<profession1b>"], ["<profession2a>"], ...],
      "ISCO": [["<isco1a>", "<isco1b>"], ["<isco2a>"], ...],
      "Love Interest": "<name or None>",
      "Love Interest Profession": ["<profession or None>"],
      "Love Interest's ISCO": ["<isco or None>"]
    }}
    """

def query_book_details(book_title, book_author, book_summary=None, book_description=None):
    """Retrieve book metadata using both GPT alone and web-enhanced GPT, then merge for best results."""

    # Step 1: Try GPT without any external context
    direct_prompt = generate_book_prompt(book_title, book_author)
    response_direct = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": direct_prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    direct_data = json.loads(response_direct.choices[0].message.content)  

    # Step 2: Fetch web search results
    search_query = f"{book_title} by {book_author} main characters and professions"
    search_results = google_search(search_query)  

    # Step 3: Try GPT with search + metadata (if available)
    search_prompt = generate_book_prompt(book_title, book_author, search_results, book_summary=book_summary, book_blurb=book_description)
    response_with_search = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": search_prompt}],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    search_data = json.loads(response_with_search.choices[0].message.content)  

    # Step 4: Merge results - prevent overuse of "Unknown"
    def is_unknown(value):
        return value in ["Unknown", None, [], "None"]

    final_data = {}
    for key in direct_data.keys():
        if is_unknown(search_data.get(key, None)):  
            # Use the AI's knowledge if search failed
            final_data[key] = direct_data[key]
        else:
            # Use search-enhanced results if they exist
            final_data[key] = search_data[key]

    return final_data  

df_books = pd.read_csv(os.path.join(config.DATA_DIR, 'books_list_with_metadata.csv'))
books = df_books.to_dict(orient="records")

OUTPUT_FILE = os.path.join(config.DATA_DIR, "book_character_professions.csv")

file_exists = os.path.isfile(OUTPUT_FILE)

if file_exists:
    df_existing = pd.read_csv(OUTPUT_FILE)
else:
    df_existing = pd.DataFrame()

# Extract already saved books for deduplication
if not df_existing.empty:
    existing_books = set(zip(df_existing["Book Title"], df_existing["Book Author"]))
else:
    existing_books = set()

max_protagonists_seen = len([col for col in df_existing.columns if "Protagonist" in col])

# Open file in append mode and process books
for i, book in enumerate(books):
    # Skip books that are already in the output CSV
    if (book["Title"], book["Author"]) in existing_books:
        print(f"Skipping {book['Title']} by {book['Author']} (already processed)")
        continue
    
    description = book["Description"] if pd.notna(book["Description"]) and book["Description"] != "Not found" else None
    summary = book["Summary"] if pd.notna(book["Summary"]) and book["Summary"] != 0 else None
    
    book_data = query_book_details(book["Title"], book["Author"], book_summary=summary, book_description=description)

    df_temp = pd.DataFrame([book_data])

    num_protagonists = len(df_temp["Protagonists"][0]) if df_temp["Protagonists"][0] else 0
    max_protagonists_seen = max(max_protagonists_seen, num_protagonists)

    for j in range(max_protagonists_seen):
        df_temp[f"Protagonist {j+1}"] = df_temp["Protagonists"].apply(lambda x: x[j] if j < len(x) else None)
        df_temp[f"Profession {j+1}"] = df_temp["Professions"].apply(lambda x: x[j] if j < len(x) else None)

    df_temp.drop(columns=["Protagonists", "Professions"], inplace=True)

    df_temp.to_csv(OUTPUT_FILE, mode="a", header=not file_exists, index=False)
    file_exists = True

    print(f"Saved: {book['Title']} by {book['Author']}")  
    time.sleep(2)