import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import time
import config 

# User credentials for Publishers Marketplace
USERNAME = 0 # Replace with actual username
PASSWORD = 0 # Replace with actual password

publisher_dict = {
                   "NYT": {"HCF", "PBF", "COF"},
                   "AMZ": {"COF"},
                   "BKS": {"PBF", "HCF"},
                   "PBW": {"HCF"}                
                }

YEAR = 2024

MONTH_MAP = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12"
}

def scrape_books(YEAR, publisher="NYT", list_type="HCF"):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")  
    options.add_argument("--disable-notifications")  # Disables push notifications
    options.add_argument("--disable-popup-blocking")  # Prevents popups
    options.add_argument("--disable-sync")  
    options.add_argument("--headless")
    
    driver = webdriver.Chrome(options=options)
    
    driver.get("https://www.publishersmarketplace.com/login.php/")
    time.sleep(2)
    
    # Enter login credentials
    driver.find_element(By.ID, "username").send_keys(USERNAME)
    driver.find_element(By.ID, "pass").send_keys(PASSWORD)
    
    driver.find_element(By.XPATH, "//input[@value='Log in']").click()
    time.sleep(3)  
    
    books = []
    month = "01"
    day = "01"

    while True:
        try:
            driver.get(f"https://www.publishersmarketplace.com/bestsellers/list.cgi?src={publisher}&lst={list_type}&pubmonth={month}&pubday={day}&pubYEAR={YEAR}")
            time.sleep(2)  

            # Find book elements in the current list
            book_elements = driver.find_elements(By.XPATH, "//td/b")

            for book in book_elements:
                title = book.text.strip()
                full_text = book.find_element(By.XPATH, "./..").text.strip()

                if ", by " in full_text:
                    author = full_text.split(", by ")[-1].split(" (")[0].strip()
                else:
                    author = "Unknown"
                
                if title.lower() in ["previous list", "next list", "current list"]:  # Remove navigation texts
                    continue
                if title.isdigit():  # Remove numbers-only entries
                    continue
                if author == "Unknown":  # Ignore short non-book titles
                    continue

                books.append((title, author))

            # Find **the last available next list date**
            next_list_elements = driver.find_elements(By.XPATH, "//span[@style='color:#009;']")
            next_list_element = next_list_elements[-1]  # Select the last date
            next_date = next_list_element.text.strip()

            # Extract month, day, and year from next_date
            month_name, day, next_year = next_date.split()
            month = MONTH_MAP[month_name]
            day = day.strip(",")

            # Stop at the end of the selected year
            if int(next_year) > YEAR:
                print(f"Reached the end of {YEAR}, stopping scrape.")
                break

        except Exception as e:
            print("No more lists available or an error occurred:", e)
            break

    
    driver.quit()
    
    df = pd.DataFrame(books, columns=["Title", "Author"]).drop_duplicates()
    return df

if __name__ == '__main__':
    for publisher, list_type in publisher_dict.items():
        for bestseller_list in list_type:
            df_books = scrape_books(year=YEAR, publisher=publisher, list_type=bestseller_list)
            df_books.to_csv(os.path.join(config.RAW_DATA_DIR, f"{publisher}_{bestseller_list}_bestsellers_{YEAR}.csv"), index=False)





