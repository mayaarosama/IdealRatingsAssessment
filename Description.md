# Overview

The main objective of this project is to extract the information of the available books from https://books.toscrape.com, and then we analyze this information in order to answer the assessment questions.
This document provides detailed descriptions of all methods in the `data_retrieval.py` and `streamlit_app.py` files for the IdealRatings Book Data Analysis Assessment project.


## Table of Contents
- [data_retrieval.py Methods](#data_retrievalpy-methods)
- [streamlit_app.py Methods](#streamlit_apppy-methods)

---

## data_retrieval.py 
This script was developed to scrape the books available on the https://books.toscrape.com website, focusing on the following categories: Travel, Mystery, Historical, Fiction, and Classics.
The main page on the website is mainly split into two sections: a sidebar menu containing all available categories, and a grid displaying all available books.
Once we select a category from the menu, the web page automatically filters the books to only display the books in the chosen category.


### `get_book_details(book_url: str) -> Dict[str, Any]`

**Purpose**: Extracts comprehensive details from a single book page.

**Parameters**:
- `book_url` (str): The complete URL of the book page to scrape

**Returns**:
- `Dict[str, Any]`: A dictionary containing all extracted book information

**Functionality**:
- Makes an HTTP request to the book page with a 10-second timeout
- Parses the HTML content using BeautifulSoup
- Extracts the following information:
  - **Description**: Product description from the product_description div
  - **Category**: Book category from the breadcrumb navigation
  - **Product Information Table**: All data from the table with class "table table-striped" (includes UPC, Price, Tax, Availability, Number of reviews, etc.)

**Error Handling**:
- Catches and logs any exceptions during scraping
- Returns an empty dictionary if extraction fails
- Provides detailed error messages for debugging

**Dependencies**:
- `requests` for HTTP requests
- `BeautifulSoup` for HTML parsing

---

### `scrape_books() -> List[Dict[str, Any]]`

**Purpose**: Scrapes all books by iterating through all available pages.

**Parameters**: None

**Returns**:
- `List[Dict[str, Any]]`: A list of dictionaries, each containing complete book information

**Functionality**:
- Iterates through all pages of the book catalog (starting from page 1)
- For each page:
  - Constructs the page URL using the BASE_URL template
  - Makes an HTTP request with a 10-second timeout
  - Parses the page to find all book articles with class "product_pod"
  - For each book article:
    - Extracts the product link and calls `get_book_details()`
    - Extracts basic information from the listing page (Title, Price, Rating)
    - Combines listing page data with detailed book data
    - Adds the complete book data to the results list
- Continues until no more articles are found or an error occurs
- Includes a 1-second delay between page requests to be respectful to the server

**Error Handling**:
- Continues processing even if individual articles fail
- Logs errors for each failed article
- Stops scraping if a page request fails
- Provides progress updates for each successfully scraped page

**Dependencies**:
- `get_book_details()` function
- `time` module for delays
- `requests` and `BeautifulSoup` for web scraping

---

### `process_book_data(books: List[Dict[str, Any]]) -> pd.DataFrame`

**Purpose**: Transforms raw scraped book data into a clean, structured DataFrame with additional calculated fields

**Parameters**:
- `books` (List[Dict[str, Any]]): Raw list of book dictionaries from scraping

**Returns**:
- `pd.DataFrame`: Processed and cleaned book data

**Functionality**:
1. **Data Filtering**:
   - Filters books to only include target categories: 'Travel', 'Mystery', 'Historical Fiction', 'Classics'
   - Selects only required columns: Title, Description, Category, Price, Rating, Availability

2. **Data Cleaning**:
   - Converts price strings to float by removing the 'Â£' symbol
   - Creates a binary availability status ('In stock' or 'Out of stock')
   - Extracts numeric availability count using regex pattern matching

3. **Feature Engineering**:
   - Calculates description length in words
   - Removes the original 'Availability' column after processing

**Data Transformations**:
- Price: `"Â£15.99"` → `15.99`
- Availability: `"In stock (22 available)"` → Status: "In stock", Count: 22
- Description: `"A great book..."` → Length: 3 (word count)

**Dependencies**:
- `pandas` for DataFrame operations
- `re` for regex pattern matching
- `TARGET_CATEGORIES` configuration constant

---

### `scrape_and_save_data() -> pd.DataFrame`

**Purpose**: Main function that coordinates the entire data scraping and processing workflow

**Parameters**: None

**Returns**:
- `pd.DataFrame`: The final processed book data

**Functionality**:
1. **Data Scraping**:
   - Calls `scrape_books()` to collect all book data
   - Displays progress information and total count

2. **Data Processing**:
   - Calls `process_book_data()` to clean and structure the data
   - Shows count of books in target categories

3. **Data Persistence**:
   - Saves the processed data to `books_details.csv` with UTF-8 encoding
   - Confirms successful save

4. **Summary Reporting**:
   - Displays category distribution statistics
   - Shows sample data preview

**Error Handling**:
- Checks if any books were successfully scraped
- Provides informative error messages if scraping fails
- Returns an empty DataFrame if no data is available

**Dependencies**:
- `scrape_books()` and `process_book_data()` functions
- `pandas` for CSV operations
- `OUTPUT_FILE` configuration constant

---

## streamlit_app.py Methods
This script was developed to answer the "Specific Questions to Address" section from the assessment PDF.
Once the data is collected and cleaned, there are three types of questions to answer: categorical_questions, numerical_questions, and hybrid_questions.
For each of those types, we provide two methods: one that analyzes the data to answer the questions and another method that is responsible for displaying the answer in the Streamlit app.

### `analyze_categorical_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]`

**Purpose**: Analyze the book dataset to answer categorical (Yes/No) questions about book availability, ratings, and pricing

**Parameters**:
- `df` (pd.DataFrame): Processed book DataFrame

**Returns**:
- `Dict[str, Dict[str, Any]]`: Dictionary containing answers and justifications for each question

**Questions Analyzed**:
1. **Travel Out of Stock**: Are there any books in the "Travel" category marked as "Out of stock"?
2. **Mystery Five Star**: Does the "Mystery" category contain books with a 5-star rating?
3. **Classics Below £10**: Are there books in the "Classics" category priced below £10?
4. **Mystery Above £20**: Are more than 50% of books in the "Mystery" category priced above £20?

**Return Structure**:
Each question result contains:
- `answer`: "Yes" or "No"
- `count`: Number of books matching the criteria
- `justification`: Detailed explanation with counts/percentages

**Dependencies**:
- `pandas` for DataFrame filtering and aggregation

---

### `analyze_numerical_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]`

**Purpose**: Performs numerical analysis on the book dataset to answer quantitative questions about pricing and availability

**Parameters**:
- `df` (pd.DataFrame): Processed book DataFrame

**Returns**:
- `Dict[str, Dict[str, Any]]`: Dictionary containing numerical results and justifications

**Questions Analyzed**:
1. **Average Prices**: What is the average price of books across each category?
2. **Historical Fiction Range**: What is the price range (min/max) for Historical Fiction books?
3. **In Stock Counts**: How many books are available in stock across the four categories?
4. **Travel Total Value**: What is the total value (sum of prices) of all Travel category books?

**Analysis Process**:
- Groups data by category
- Calculates statistical measures (min, max, mean, sum) for prices
- Counts availability by category
- Provides detailed justifications for each calculation

**Return Structure**:
- `values`: Dictionary of calculated values by category
- `justification`: Explanation of the calculation method

**Dependencies**:
- `pandas` for grouping and aggregation operations

---

### `analyze_hybrid_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]`

**Purpose**: Performs complex hybrid analysis combining categorical and numerical data to answer comparative questions

**Parameters**:
- `df` (pd.DataFrame): Processed book DataFrame

**Returns**:
- `Dict[str, Dict[str, Any]]`: Dictionary containing hybrid analysis results

**Questions Analyzed**:
1. **Highest Average Price**: Which category has the highest average price?
2. **Categories Above £30**: Which categories have more than 50% of books priced above £30?
3. **Description Length Comparison**: Compare average description length across categories
4. **Highest Out-of-Stock Percentage**: Which category has the highest percentage of out-of-stock books?

**Analysis Features**:
- **Comparative Analysis**: Compares categories against each other
- **Percentage Calculations**: Calculates percentages for threshold-based questions
- **Multi-criteria Filtering**: Applies multiple conditions simultaneously
- **Ranking Operations**: Identifies top-performing categories

**Return Structure**:
- `category`: Single category name for winner-type questions
- `categories`: List of categories meeting criteria
- `values`: Dictionary of values by category
- `justification`: Detailed explanation of analysis method

**Dependencies**:
- `pandas` for complex grouping and filtering operations

---

### `show_dataset_overview(df)`

**Purpose**: Displays a comprehensive overview of the dataset in the Streamlit interface

**Parameters**:
- `df`: Processed book DataFrame

**Returns**: None (displays UI components)

**UI Components**:
1. **Key Metrics** (4-column layout):
   - Total number of books
   - Number of unique categories
   - Average price across all books
   - Price range (min to max)

2. **Visualizations**:
   - Bar chart showing category distribution
   - Bar chart showing price distribution

3. **Data Preview**:
   - Interactive table showing first 10 rows of data

**Dependencies**:
- `streamlit` for UI components
- `pandas` for data operations

---

### `show_categorical_questions(df)`

**Purpose**: Displays categorical question analysis results in an interactive Streamlit interface

**Parameters**:
- `df`: Processed book DataFrame

**Returns**: None (displays UI components)

**UI Features**:
- **Expandable Questions**: Each question is displayed in a collapsible expander
- **Answer Display**: Clear Yes/No answers with visual emphasis
- **Detailed Justifications**: Complete explanations of the analysis
- **Supporting Data**: Shows counts and percentages where relevant

**Question Format**:
- Question text as expander title
- Answer with bold formatting
- Justification paragraph
- Additional metrics (counts, percentages)

**Dependencies**:
- `analyze_categorical_questions()` function
- `streamlit` for UI components

---

### `show_numerical_questions(df)`

**Purpose**: Displays numerical question analysis results in the Streamlit interface

**Parameters**:
- `df`: Processed book DataFrame

**Returns**: None (displays UI components)

**UI Features**:
- **Expandable Questions**: Each question in a collapsible section
- **Value Display**: Shows calculated numerical values
- **Justification**: Explains the calculation methodology
- **Structured Data**: Organizes values by category when applicable

**Data Presentation**:
- Single values displayed prominently
- Multi-value results shown as bulleted lists
- Category-specific values clearly labeled

**Dependencies**:
- `analyze_numerical_questions()` function
- `streamlit` for UI components

---

### `show_hybrid_questions(df)`

**Purpose**: Displays hybrid question analysis results in the Streamlit interface

**Parameters**:
- `df`: Processed book DataFrame

**Returns**: None (displays UI components)

**UI Features**:
- **Complex Results**: Handles both single and multiple result types
- **Category Comparisons**: Shows comparative analysis between categories
- **Percentage Displays**: Formats percentage results clearly
- **Detailed Breakdowns**: Shows counts and totals for complex questions

**Result Types Handled**:
- Single category winners
- Multiple categories meeting criteria
- Percentage-based rankings
- Comparative value displays

**Dependencies**:
- `analyze_hybrid_questions()` function
- `streamlit` for UI components

---

### `main()`

**Purpose**: Main application entry point that orchestrates the entire Streamlit application

**Parameters**: None

**Returns**: None

**Application Features**:
1. **Page Configuration**:
   - Sets page title, icon, and layout
   - Configures wide layout for better data display

2. **Data Loading**:
   - Implements cached data loading for performance
   - Checks for existing CSV file first
   - Falls back to fresh scraping if no data exists
   - Handles data loading errors gracefully

3. **Navigation System**:
   - Sidebar navigation with page selection
   - Data refresh functionality
   - Four main analysis pages

4. **Page Routing**:
   - Routes to appropriate analysis page based on selection
   - Handles missing or empty data scenarios

**Caching Strategy**:
- Uses `@st.cache_data` for data loading
- Provides manual cache clearing via refresh button
- Improves performance for repeated data access

**Error Handling**:
- Comprehensive error handling for data loading
- User-friendly error messages
- Graceful fallback to data scraping

**Dependencies**:
- All analysis functions (`show_*` methods)
- `load_data()` cached function
- `streamlit` for application framework

---

## Configuration Constants

### data_retrieval.py
- `BASE_URL`: Template URL for paginated book listings
- `BASE_SITE`: Base URL for individual book pages
- `OUTPUT_FILE`: CSV filename for saved data
- `TARGET_CATEGORIES`: List of categories to include in analysis

### streamlit_app.py
- Page configuration settings
- UI layout preferences
- Data file paths

---

## Dependencies Summary

### External Libraries
- `requests`: HTTP requests for web scraping
- `beautifulsoup4`: HTML parsing
- `pandas`: Data manipulation and analysis
- `streamlit`: Web application framework
- `numpy`: Numerical operations

### Internal Dependencies
- `data_retrieval` module functions
- Configuration constants
- Type hints from `typing` module

---

## Error Handling Strategy

### data_retrieval.py
- Network timeout handling (10-second timeouts)
- Graceful degradation for individual book failures
- Comprehensive logging for debugging
- Empty result handling

### streamlit_app.py
- Data loading error handling
- User-friendly error messages
- Graceful fallback to data scraping
- Cache management for data refresh

---
