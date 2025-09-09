import requests
import time
import pandas as pd
import config

GOOGLE_BOOKS_API_KEY = 0  # Replace with key from https://console.cloud.google.com/

def fetch_google_books_metadata(title, author):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"intitle:{title} inauthor:{author}",
        "key": GOOGLE_BOOKS_API_KEY,
        "maxResults": 1
    }
    
    response = requests.get(base_url, params=params)
    if response.status_code != 200:
        return None

    data = response.json()
    if "items" not in data:
        return None

    book_info = data["items"][0]["volumeInfo"]

    # Extract metadata
    genres = ", ".join(book_info.get("categories", ["N/A"]))
    description = book_info.get("description", "N/A")

    return {
        "Title": title,
        "Author": author,
        "Genres": genres,
        "Description": description
    }

# Load book list from CSV
input_file = os.path.join(config.RAW_DATA_DIR, "combined_nyt_books.csv")
existing_metadata_file = os.path.join(config.DATA_DIR, "book_list_with_metadata.csv")
output_file = os.path.join(config.DATA_DIR, "nyt_books_with_google_metadata.csv")

df = pd.read_csv(input_file, dtype=str)
df_existing = pd.read_csv(existing_metadata_file)

existing_metadata_dict = {
    (row["Title"], row["Author"]): row.to_dict()
    for _, row in df_existing.iterrows()
}

# Ensure required columns exist
if not {"Title", "Author"}.issubset(df.columns):
    raise ValueError("CSV must contain 'Title' and 'Author' columns")

# Fetch metadata for each book
metadata_list = []
for _, row in df.iterrows():
    title, author = row["Title"], row["Author"]
    if (title, author) in existing_metadata_dict:
        print(f"Found existing metadata for: {title} by {author}")
        metadata_list.append(existing_metadata_dict[(title, author)])
    else:
        print(f"Fetching metadata for: {title} by {author}")
        metadata = fetch_google_books_metadata(title, author)
        
    if metadata:
        metadata_list.append(metadata)
    else:
        metadata_list.append({
            "Title": title,
            "Author": author,
            "Genres": "Not Found",
            "Description": "Not Found"
        })
    
    time.sleep(1)  

# Save results to a new CSV file
output_df = pd.DataFrame(metadata_list)
output_df.to_csv(output_file, index=False)

print(f"Metadata saved to {output_file}")


