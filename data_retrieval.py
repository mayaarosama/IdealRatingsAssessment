import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from typing import List, Dict, Any

# Configuration
BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
BASE_SITE = "https://books.toscrape.com/catalogue/"
OUTPUT_FILE = "books_details.csv"
TARGET_CATEGORIES = ['Travel', 'Mystery', 'Historical Fiction', 'Classics']

def get_book_details(book_url: str) -> Dict[str, Any]:
    """
    Extract all details dynamically from a single book page.
    
    Args:
        book_url: URL of the book page to scrape
        
    Returns:
        Dict containing book details
    """
    try:
        response = requests.get(book_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        book_data = {}

        # Description
        description_tag = soup.find("div", id="product_description")
        book_data["Description"] = (
            description_tag.find_next_sibling("p").get_text(strip=True)
            if description_tag else "No description available"
        )

        # Category
        breadcrumb = soup.find("ul", class_="breadcrumb")
        if breadcrumb:
            breadcrumb_items = breadcrumb.find_all("li")
            book_data["Category"] = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) > 2 else "Unknown"
        else:
            book_data["Category"] = "Unknown"

        # Product Information Table (dynamic)
        table = soup.find("table", class_="table table-striped")
        if table:
            for row in table.find_all("tr"):
                key = row.th.get_text(strip=True)
                value = row.td.get_text(strip=True)
                book_data[key] = value

        return book_data
    except Exception as e:
        print(f"Error scraping book details from {book_url}: {e}")
        return {}

def scrape_books() -> List[Dict[str, Any]]:
    """
    Scrape all books from books.toscrape.com
    
    Returns:
        List of book dictionaries
    """
    books = []
    page = 1

    while True:
        url = BASE_URL.format(page)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code != 200:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article", class_="product_pod")
            if not articles:
                break

            for article in articles:
                try:
                    product_link = BASE_SITE + article.h3.a["href"]
                    book_data = get_book_details(product_link)
                    
                    # Listing page data
                    book_data["Title"] = article.h3.a["title"]
                    book_data["Price"] = article.find("p", class_="price_color").text.strip()
                    book_data["Rating"] = article.p["class"][1]
                    book_data["Product Link"] = product_link

                    books.append(book_data)
                except Exception as e:
                    print(f"Error processing article: {e}")
                    continue

            print(f"Scraped page {page}")
            page += 1
            time.sleep(1)  # Be respectful to the server
            
        except Exception as e:
            print(f"Error scraping page {page}: {e}")
            break

    return books

def process_book_data(books: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Process raw book data into a clean DataFrame.
    
    Args:
        books: List of book dictionaries
        
    Returns:
        pd.DataFrame: Processed book data
    """
    df = pd.DataFrame(books)
    
    # Filter for target categories
    df = df[df['Category'].isin(TARGET_CATEGORIES)]
    
    # Select required columns
    df = df[['Title', 'Description', 'Category', 'Price', 'Rating', 'Availability']].copy()
    
    # Convert price to float
    df['Price'] = df['Price'].astype(str).str.replace('Â£', '', regex=False).astype(float)
    
    # Process availability
    df["Availability Status"] = df["Availability"].apply(
        lambda x: "In stock" if "In stock" in str(x) else "Out of stock"
    )
    
    # Extract numeric availability count
    df["Availability_Count"] = df["Availability"].apply(
        lambda x: int(re.search(r'\d+', str(x)).group()) if re.search(r'\d+', str(x)) else 0
    )
    
    # Calculate description length
    df['Description Length'] = df['Description'].apply(
        lambda x: len(str(x).split()) if isinstance(x, str) else 0
    )
    
    df.drop(columns=['Availability'], inplace=True)
    
    return df

def scrape_and_save_data() -> pd.DataFrame:
    """
    Scrape books data and save to CSV file.
    
    Returns:
        pd.DataFrame: Processed book data
    """
    print("Starting book data scraping...")
    books = scrape_books()
    print(f"Total books scraped: {len(books)}")
    
    if not books:
        print("No books were scraped. Please check your internet connection and try again.")
        return pd.DataFrame()
    
    # Process the data
    df = process_book_data(books)
    print(f"Books in target categories: {len(df)}")
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"Data saved to {OUTPUT_FILE}")
    
    # Display summary
    print("\nCategory distribution:")
    print(df['Category'].value_counts())
    
    return df

if __name__ == "__main__":
    # Run the scraping process
    df = scrape_and_save_data()
    if not df.empty:
        print("\nSample data:")
        print(df.head())
