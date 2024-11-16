import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st

# Function to scrape city names and weather details
def scrape_cities_and_details(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, f"Error: Unable to fetch the webpage. Status code {response.status_code}."
    
    soup = BeautifulSoup(response.content, "html.parser")
    cities = []
    details = []
    
    # Scrape city names
    city_elements = soup.select(".b-list-table a")

    target_divs = soup.find_all('div', {'class': 'smallweathercell'})
    for div in target_divs:
        img_tag = div.find('img')
        if img_tag:
            alt_text = img_tag.get('alt')
            details.append(alt_text)

        
    # Combine city names and their respective details
    for city in city_elements:
        cities.append(city.text.strip())        
    
    # Create a DataFrame
    data = pd.DataFrame({"City": cities, "Details": details})
    return data, None

def main():
    st.title("Weather Forecast: Cities in Pakistan (Sortable, Searchable)")

    url = "https://www.weather-forecast.com/countries/Pakistan"
    st.write(f"Fetching data from [Weather Forecast]({url})...")

    # Scrape data
    weather_data, error_message = scrape_cities_and_details(url)

    if error_message:
        st.error(error_message)
    else:
        st.success(f"Found {len(weather_data)} cities!")
        st.write("### Weather Details (Sortable, Searchable):")

        # Add search bar
        search_query = st.text_input("Search for a city:")

        # Filter data based on search query
        if search_query:
            filtered_data = weather_data[weather_data['City'].str.contains(search_query, case=False)]
        else:
            filtered_data = weather_data

        # Split the "Details" column into "Condition" and "Temperature (C)"
        filtered_data[['Condition', 'Temperature (C)']] = filtered_data['Details'].str.split(' and ', expand=True)
        filtered_data.drop('Details', axis=1, inplace=True)

        # Show only first 4 characters in "Temperature (C)"
        filtered_data['Temperature (C)'] = filtered_data['Temperature (C)'].str[:5]

        # Add sorting selectbox
        sort_by = st.selectbox("Sort by:", ["City", "Condition", "Temperature (C)"])

        # Sort data based on user selection
        if sort_by:
            filtered_data = filtered_data.sort_values(by=sort_by)

        # Display data in a styled table
        st.markdown(
            filtered_data.to_html(index=False, classes="styled-table"),
            unsafe_allow_html=True,
        )
        # Add CSS for table styling
        st.markdown("""
            <style>
            .styled-table {
                border-collapse: collapse;
                margin: 25px 0;
                font-size: 1.2em;
                font-family: Arial, sans-serif;
                min-width: 400px;
                border-radius: 5px 5px 0 0;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
            }
            .styled-table thead tr {
                background-color: #009879;
                color: #ffffff;
                text-align: left;
                font-weight: bold;
            }
            .styled-table th {                
                text-align: center;
            }
            .styled-table th, .styled-table td {
                padding: 12px 15px;            
            }
            .styled-table tbody tr {
                border-bottom: 1px solid #dddddd;
            }
            .styled-table tbody tr:nth-of-type(even) {
                background-color: #f3f3f3;
            }
            .styled-table tbody tr:last-of-type {
                border-bottom: 2px solid #009879;
            }
            </style>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
