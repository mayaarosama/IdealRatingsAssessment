import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import re
import os
from data_retrieval import scrape_and_save_data, process_book_data


def analyze_categorical_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Answer categorical (Yes/No) questions with justification.
    
    Args:
        df: Processed book DataFrame
        
    Returns:
        Dict containing answers and justifications
    """
    results = {}
    
    # Question 1: Are there any books in the "Travel" category that are marked as "Out of stock"?
    travel_out_of_stock = df[(df['Category'] == 'Travel') & (df['Availability Status'] == 'Out of stock')]
    results['travel_out_of_stock'] = {
        'answer': 'Yes' if len(travel_out_of_stock) > 0 else 'No',
        'count': len(travel_out_of_stock),
        'justification': f"Found {len(travel_out_of_stock)} books in Travel category marked as 'Out of stock'"
    }
    
    # Question 2: Does the "Mystery" category contain books with a 5-star rating?
    mystery_five_star = df[(df['Category'] == 'Mystery') & (df['Rating'] == 'Five')]
    results['mystery_five_star'] = {
        'answer': 'Yes' if len(mystery_five_star) > 0 else 'No',
        'count': len(mystery_five_star),
        'justification': f"Found {len(mystery_five_star)} books in Mystery category with 5-star rating"
    }
    
    # Question 3: Are there books in the "Classics" category priced below £10?
    classics_below_10 = df[(df['Category'] == 'Classics') & (df['Price'] < 10)]
    results['classics_below_10'] = {
        'answer': 'Yes' if len(classics_below_10) > 0 else 'No',
        'count': len(classics_below_10),
        'justification': f"Found {len(classics_below_10)} books in Classics category priced below £10"
    }
    
    # Question 4: Are more than 50% of books in the "Mystery" category priced above £20?
    mystery_books = df[df['Category'] == 'Mystery']
    mystery_above_20 = mystery_books[mystery_books['Price'] > 20]
    percentage_above_20 = (len(mystery_above_20) / len(mystery_books)) * 100 if len(mystery_books) > 0 else 0
    results['mystery_above_20_percent'] = {
        'answer': 'Yes' if percentage_above_20 > 50 else 'No',
        'percentage': percentage_above_20,
        'justification': f"{percentage_above_20:.1f}% of Mystery books are priced above £20"
    }
    
    return results

def analyze_numerical_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Answer numerical questions with extracted values and justification.
    
    Args:
        df: Processed book DataFrame
        
    Returns:
        Dict containing numerical answers and justifications
    """
    results = {}
    
    # Calculate grouped statistics
    df_grouped = df.groupby('Category').agg({
        'Price': ['min', 'max', 'mean', 'sum'],
        'Availability_Count': 'sum',
        'Description Length': 'mean'
    }).round(2)
    
    # Question 1: Average price by category
    avg_prices = df_grouped['Price']['mean']
    results['average_prices'] = {
        'values': avg_prices.to_dict(),
        'justification': "Calculated mean price for each category from all available books"
    }
    
    # Question 2: Price range for Historical Fiction
    hist_fiction_min = df_grouped.loc['Historical Fiction', ('Price', 'min')]
    hist_fiction_max = df_grouped.loc['Historical Fiction', ('Price', 'max')]
    results['historical_fiction_price_range'] = {
        'min_price': hist_fiction_min,
        'max_price': hist_fiction_max,
        'justification': f"Price range for Historical Fiction: £{hist_fiction_min} - £{hist_fiction_max}"
    }
    
    # Question 3: Books in stock by category
    in_stock_counts = df[df['Availability Status'] == 'In stock'].groupby('Category').size()
    results['in_stock_counts'] = {
        'values': in_stock_counts.to_dict(),
        'justification': "Count of books marked as 'In stock' for each category"
    }
    
    # Question 4: Total value of Travel category
    travel_total_value = df_grouped.loc['Travel', ('Price', 'sum')]
    results['travel_total_value'] = {
        'value': travel_total_value,
        'justification': f"Sum of all book prices in Travel category: £{travel_total_value}"
    }
    
    return results

def analyze_hybrid_questions(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Answer hybrid questions.
    
    Args:
        df: Processed book DataFrame
        
    Returns:
        Dict containing hybrid answers and justifications
    """
    results = {}
    
    # Calculate grouped statistics
    df_grouped = df.groupby('Category').agg({
        'Price': ['min', 'max', 'mean', 'sum'],
        'Availability_Count': 'sum',
        'Description Length': 'mean'
    }).round(2)
    
    # Question 1: Category with highest average price
    highest_avg_price_category = df_grouped['Price']['mean'].idxmax()
    highest_avg_price_value = df_grouped['Price']['mean'].max()
    results['highest_avg_price_category'] = {
        'category': highest_avg_price_category,
        'average_price': highest_avg_price_value,
        'justification': f"{highest_avg_price_category} has the highest average price at £{highest_avg_price_value}"
    }
    
    # Question 2: Categories with >50% books above £30
    categories_above_30_percent = []
    for category in df['Category'].unique():
        category_df = df[df['Category'] == category]
        total_books = len(category_df)
        books_above_30 = len(category_df[category_df['Price'] > 30])
        percentage = (books_above_30 / total_books) * 100 if total_books > 0 else 0
        
        if percentage > 50:
            categories_above_30_percent.append({
                'category': category,
                'percentage': percentage,
                'count': books_above_30,
                'total': total_books
            })
    
    results['categories_above_30_percent'] = {
        'categories': categories_above_30_percent,
        'justification': f"Found {len(categories_above_30_percent)} categories with >50% books above £30"
    }
    
    # Question 3: Average description length by category
    avg_description_lengths = df_grouped['Description Length']['mean']
    results['average_description_lengths'] = {
        'values': avg_description_lengths.to_dict(),
        'justification': "Average word count in book descriptions by category"
    }
    
    # Question 4: Category with highest percentage of out-of-stock books
    out_of_stock_counts = df[df['Availability Status'] == 'Out of stock'].groupby('Category').size()
    total_counts = df.groupby('Category').size()
    out_of_stock_percentages = (out_of_stock_counts / total_counts * 100).fillna(0)
    
    if out_of_stock_percentages.max() > 0:
        highest_percentage_category = out_of_stock_percentages.idxmax()
        highest_percentage_value = out_of_stock_percentages.max()
        results['highest_out_of_stock_percentage'] = {
            'category': highest_percentage_category,
            'percentage': highest_percentage_value,
            'justification': f"{highest_percentage_category} has the highest percentage of out-of-stock books at {highest_percentage_value:.1f}%"
        }
    else:
        results['highest_out_of_stock_percentage'] = {
            'category': 'None',
            'percentage': 0,
            'justification': "No books found marked as out of stock"
        }
    
    return results

def show_dataset_overview(df):
    """Display dataset overview page."""
    st.header("Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Books", len(df))
    with col2:
        st.metric("Categories", len(df['Category'].unique()))
    with col3:
        st.metric("Avg Price", f"£{df['Price'].mean():.2f}")
    with col4:
        st.metric("Price Range", f"£{df['Price'].min():.2f} - £{df['Price'].max():.2f}")
    
    # Category distribution
    st.subheader("Category Distribution")
    category_counts = df['Category'].value_counts()
    st.bar_chart(category_counts)
    
    # Price distribution
    st.subheader("Price Distribution")
    st.bar_chart(df['Price'])
    
    # Sample data
    st.subheader("Sample Data")
    st.dataframe(df.head(10))

def show_categorical_questions(df):
    """Display categorical questions page."""
    st.header("Categorical Questions (Yes/No)")
    
    categorical_results = analyze_categorical_questions(df)
    
    questions = [
        "Are there any books in the 'Travel' category that are marked as 'Out of stock'?",
        "Does the 'Mystery' category contain books with a 5-star rating?",
        "Are there books in the 'Classics' category priced below £10?",
        "Are more than 50% of books in the 'Mystery' category priced above £20?"
    ]
    
    for i, (question, result) in enumerate(zip(questions, categorical_results.values())):
        with st.expander(f"Question {i+1}: {question}"):
            st.write(f"**Answer:** {result['answer']}")
            st.write(f"**Justification:** {result['justification']}")
            if 'count' in result:
                st.write(f"**Count:** {result['count']}")
            if 'percentage' in result:
                st.write(f"**Percentage:** {result['percentage']:.1f}%")

def show_numerical_questions(df):
    """Display numerical questions page."""
    st.header("Numerical Questions")
    
    numerical_results = analyze_numerical_questions(df)
    
    questions = [
        "What is the average price of books across each category?",
        "What is the price range (minimum and maximum) for books in the 'Historical Fiction' category?",
        "How many books are available in stock across the four categories?",
        "What is the total value (sum of prices) of all books in the 'Travel' category?"
    ]
    
    for i, (question, result) in enumerate(zip(questions, numerical_results.values())):
        with st.expander(f"Question {i+1}: {question}"):
            st.write(f"**Justification:** {result['justification']}")
            if 'values' in result:
                st.write("**Values:**")
                for key, value in result['values'].items():
                    st.write(f"  - {key}: {value}")
            else:
                st.write(f"**Value:** {result.get('value', result.get('min_price', 'max_price'))}")

def show_hybrid_questions(df):
    """Display hybrid questions page."""
    st.header("Hybrid Questions")
    
    hybrid_results = analyze_hybrid_questions(df)
    
    questions = [
        "Which category has the highest average price of books?",
        "Which categories have more than 50% of their books priced above £30?",
        "Compare the average description length (in words) across the four categories.",
        "Which category has the highest percentage of books marked as 'Out of stock'?"
    ]
    
    for i, (question, result) in enumerate(zip(questions, hybrid_results.values())):
        with st.expander(f"Question {i+1}: {question}"):
            st.write(f"**Justification:** {result['justification']}")
            if 'category' in result:
                st.write(f"**Category:** {result['category']}")
            if 'categories' in result:
                st.write("**Categories:**")
                for cat_info in result['categories']:
                    st.write(f"  - {cat_info['category']}: {cat_info['percentage']:.1f}% ({cat_info['count']}/{cat_info['total']} books)")
            if 'values' in result:
                st.write("**Values:**")
                for key, value in result['values'].items():
                    st.write(f"  - {key}: {value}")


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Book Data Analysis - IdealRatings Assessment",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Book Data Analysis System")
    st.markdown("**IdealRatings Assessment - Books.toscrape.com Analysis**")
    
    # Load data
    @st.cache_data
    def load_data():
        # Check if data file exists
        if os.path.exists("books_details.csv"):
            try:
                df = pd.read_csv("books_details.csv")
                # Data is already processed, just return it
                return df
            except Exception as e:
                st.error(f"Error loading existing data: {e}")
                return None
        else:
            # Data file doesn't exist, scrape new data
            st.info("No data file found. Scraping fresh data from books.toscrape.com...")
            try:
                df = scrape_and_save_data()
                return df
            except Exception as e:
                st.error(f"Error scraping data: {e}")
                return None
    
    df = load_data()
    if df is None or df.empty:
        st.error("Failed to load data. Please check your internet connection and try again.")
        return
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    # Data refresh button
    if st.sidebar.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Dataset Overview", "Categorical Questions", "Numerical Questions", "Hybrid Questions"]
    )
    
    # Page content based on selection
    if page == "Dataset Overview":
        show_dataset_overview(df)
    elif page == "Categorical Questions":
        show_categorical_questions(df)
    elif page == "Numerical Questions":
        show_numerical_questions(df)
    elif page == "Hybrid Questions":
        show_hybrid_questions(df)
    

if __name__ == "__main__":
    main()
