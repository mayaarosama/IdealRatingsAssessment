# Book Data Analysis System - IdealRatings Assessment

A comprehensive data analysis system for extracting and analyzing book information from books.toscrape.com, specifically focusing on Travel, Mystery, Historical Fiction, and Classics categories.

## Project Overview

This project implements a complete data pipeline that:
- Scrapes book data from books.toscrape.com
- Processes and cleans the data
- Provides interactive analysis through a Streamlit web interface
- Answers specific categorical, numerical, and hybrid questions about the book dataset

## Features

- **Data Scraping**: Automated web scraping of book details
- **Data Processing**: Clean and structured data preparation
- **Interactive Analysis**: Streamlit-based web interface
- **Question Types**:
  - Categorical (Yes/No) questions with justifications
  - Numerical analysis with extracted values
  - Hybrid questions combining categorical and numerical analysis

## Project Structure

```
streamlit_app.py          # Main Streamlit web application
data_retrieval.py         # Data scraping and processing module
requirements.txt          # Python dependencies
README.md                # This file
```

## Installation & Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/mayaarosama/IdealRatingsAssessment.git
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

If you encounter issues with specific packages, install them individually:

```bash
pip install streamlit pandas numpy requests beautifulsoup4 lxml
```

### Step 3: Generate Data (Optional)

The application will automatically scrape data from books.toscrape.com when first run. If you want to generate data manually:

```bash
python data_retrieval.py
```

## Running the Application

```bash
python -m streamlit run streamlit_app.py
```

## Accessing the Application

Open your web browser and navigate to `http://localhost:8501` to access the application.

## Application Features

### 1. Dataset Overview
- Total books count
- Category distribution
- Price statistics
- Sample data preview

### 2. Categorical Questions (Yes/No)
- Are there any books in the "Travel" category that are marked as "Out of stock"?
- Does the "Mystery" category contain books with a 5-star rating?
- Are there books in the "Classics" category priced below £10?
- Are more than 50% of books in the "Mystery" category priced above £20?

### 3. Numerical Questions
- Average price by category
- Price range for Historical Fiction
- Books in stock by category
- Total value of Travel category

### 4. Hybrid Questions
- Category with highest average price
- Categories with >50% books above £30
- Average description length by category
- Category with highest out-of-stock percentage

## Data Schema

The generated CSV file contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| Title | String | Book title |
| Category | String | Book category (Travel, Mystery, Historical Fiction, Classics) |
| Price | String | Book price in £ |
| Availability | String | Stock availability status |
| Rating | String | Star rating (One, Two, Three, Four, Five) |
| Description | String | Book description text |

## Analysis Capabilities

The system can answer various types of questions:

- **Categorical Analysis**: Yes/No questions with statistical justification
- **Numerical Analysis**: Statistical calculations and aggregations
- **Hybrid Analysis**: Cross-category comparisons

##  Technical Details

### Key Technologies
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **BeautifulSoup**: Web scraping
- **NumPy**: Numerical computing
- **Requests**: HTTP library

**Note**: This application is designed for assessment purposes.

