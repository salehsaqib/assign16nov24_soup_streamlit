import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Function to scrape latest news from Dawn
def fetch_dawn_news():
    url = 'https://www.dawn.com/latest-news'
    
    # Request headers to mimic a browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send GET request to the page
    response = requests.get(url, headers=headers)

    # If the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all the article links (assuming articles are in <div> with class 'story__content')
        articles = soup.find_all('div', class_='sm:w-2/3 w-full sm:ml-6 sm:border-b border-gray-200')

        news_data = []

        # Extract relevant information from each article
        for article in articles:
            title_tag = article.find('a', class_='story__link')
            summary_tag = article.find('div', class_='story__excerpt')
            timestamp_tag = article.find('span', class_='timestamp--time timeago')

            if title_tag:
                title = title_tag.get_text(strip=True)
                link = title_tag['href']
                summary = summary_tag.get_text(strip=True) if summary_tag else "No summary available"
                # Extract the published time if available
                published_time = timestamp_tag.get_text(strip=True) if timestamp_tag else "Not available"
                
                # Append the article details to the news_data list
                news_data.append({
                    'Title': title,
                    'Summary': summary,
                    'Published Time': published_time,
                    'Link': f'https://www.dawn.com{link}'  # Complete the URL
                })
        
        return news_data
    else:
        st.error(f"Failed to retrieve news. Status code: {response.status_code}")
        return []

# Streamlit UI function
# Streamlit UI function
def main():
    # Set up the Streamlit page title
    st.title("Dawn News - Latest Updates")
    st.markdown("## Latest News from Dawn")

    # Fetch news articles
    news_data = fetch_dawn_news()

    # Title search filter
    title_search = st.text_input("Search by title", "")

    # Apply title filter
    if title_search:
        filtered_data = [article for article in news_data if title_search.lower() in article['Title'].lower()]
    else:
        filtered_data = news_data

    # Published time filter
    time_filter = st.selectbox("Filter by published time", ["All", "Today", "Last 24 hours", "Older"])

    # Function to check if article's published time matches the filter
    def time_filter_match(article, filter_option):
        if filter_option == "All":
            return True
        elif filter_option == "Today" and "hours ago" in article['Published Time']:
            return True
        elif filter_option == "Last 24 hours" and "hour" in article['Published Time']:
            return True
        elif filter_option == "Older" and not any(word in article['Published Time'] for word in ["hours ago", "hour"]):
            return True
        return False

    # Apply time filter
    filtered_data = [article for article in filtered_data if time_filter_match(article, time_filter)]

    # Display filtered data
    if filtered_data:
        news_df = pd.DataFrame(filtered_data)
        st.dataframe(news_df)
    else:
        st.write("No articles found with the given filters.")


# Run the app
if __name__ == "__main__":
    main()
