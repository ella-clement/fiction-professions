import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import config

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")  # Run in background for speed
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# CSV file path
CSV_FILE = os.path.join(config.DATA_DIR, "book_list_with_metadata.csv")

def search_supersummary(title, author):
    """Search for a book on SuperSummary from the current page and return the correct result URL if found."""
    try:
        # Check if the search box exists on the current page, otherwise reload SuperSummary homepage
        search_box = driver.find_element(By.ID, "searchFieldAppBar")
    except:
        driver.get("https://www.supersummary.com/")
        time.sleep(3)
        search_box = driver.find_element(By.ID, "searchFieldAppBar")

    # Clear the search box and enter the new query
    search_box.clear()
    search_box.send_keys(f"{title}, {author}")
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)

    book_titles = driver.find_elements(By.XPATH, "//span[contains(@class, 'MuiTypography-titleL')]")
    book_authors = driver.find_elements(By.XPATH, "//p[contains(@class, 'MuiTypography-bodyM')]")

    for i in range(min(len(book_titles), len(book_authors))):
        found_title = book_titles[i].text.strip().lower()
        found_author = book_authors[i].text.strip().lower()

        def clean_text(text):
            return re.sub(r"[^a-z0-9]", "", text.lower())

        if clean_text(title) == clean_text(found_title) and clean_text(author) == clean_text(found_author):
            book_link = book_titles[i].find_element(By.XPATH, "./ancestor::a").get_attribute("href")
            print(f"Found match: {found_title} by {found_author}")
            return book_link

    print(f"No match for '{title}' by '{author}'.")
    return None

def scrape_supersummary_plot(book_url):
    """Scrape the full plot summary from the SuperSummary book page."""
    driver.get(book_url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//strong[contains(text(), 'Plot Summary')]"))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
        plot_header = soup.find(lambda tag: tag.name in ["strong", "h2", "h3"] and "Plot Summary" in tag.text)

        if not plot_header:
            print("Plot summary section not found.")
            return None

        plot_summary = []
        for sibling in plot_header.find_all_next():
            if sibling.name in ["h2", "h3", "strong"] and sibling.text.strip() != "Plot Summary":
                break
            if sibling.name == "p":
                plot_summary.append(sibling.get_text(strip=True))

        return " ".join(plot_summary) if plot_summary else None

    except Exception as e:
        print(f"Error extracting summary: {e}")
        return None

def get_supersummary_summary(title, author):
    """Check SuperSummary and scrape the plot summary."""
    book_url = search_supersummary(title, author)
    if book_url:
        return scrape_supersummary_plot(book_url)
    return None

def update_csv_with_summaries(csv_file):
    """Read the CSV, check for missing summaries, and update it batch-by-batch."""
    if not os.path.exists(csv_file):
        print("CSV file not found.")
        return

    df = pd.read_csv(csv_file)

    if "Summary" not in df.columns:
        df["Summary"] = ""

    for i, row in df.iterrows():
        if pd.isna(row["Summary"]) or row["Summary"] == "":
            print(f"\n Searching for: {row['Title']} by {row['Author']}")

            summary = get_supersummary_summary(row["Title"], row["Author"])
            if summary:
                df.at[i, "Summary"] = summary
                print(f"Summary added for: {row['Title']}")
            else:
                df.at[i, "Summary"] = "0"  # Mark as not found to avoid re-searching

            # Save progress after each book
            df.to_csv(csv_file, index=False)

            time.sleep(2)  

    print("All books processed!")

update_csv_with_summaries(CSV_FILE)

driver.quit()
