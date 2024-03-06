import streamlit as st
from google.cloud import bigquery
import requests

# Set your Google Cloud credentials
# Make sure to replace 'path/to/your/service-account-file.json' with the path to your service account key file
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Laurent Sierro\Documents\Clef_Gcloud\kamboo-creek-415115-6445343d2370.json"

# Initialize a BigQuery client
client = bigquery.Client()

def fetch_genres():
    query = """
        SELECT DISTINCT genres
        FROM `bamboo-creek-415115.movie_rating.movies_description`
    """
    query_job = client.query(query)
    results = query_job.result()
    unique_genres = set(genre for row in results for genre in row['genres'].split('|'))
    return sorted(unique_genres)

def fetch_languages():
    query = """
        SELECT DISTINCT language
        FROM `bamboo-creek-415115.movie_rating.movies_description`
    """
    query_job = client.query(query)
    results = query_job.result()
    unique_languages = [row['language'] for row in results]
    return sorted(unique_languages)

# Function to fetch movies by genre
def fetch_movies(genre, language):
    # Base query
    query = """
        SELECT title
        FROM `bamboo-creek-415115.movie_rating.movies_description`
    """
    conditions = []
    
    if genre != 'Select a genre':
        conditions.append(f"genres LIKE '%{genre}%'")
    

    if language != 'Select a language':
        conditions.append(f"language = '{language}'")
        

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += """
        ORDER BY title
        LIMIT 20
    """
    print("Final Query:", query)
    
    query_job = client.query(query)
    results = query_job.result()
    return results

# Streamlit interface
st.title('Movie Finder')

# Dropdown to select genre
genre_options = ['Select a genre'] + fetch_genres()
genre_options.remove('(no genres listed)')
genre = st.selectbox('Choose a genre', genre_options, index=0)

language_options = ['Select a language'] + fetch_languages()
language=st.selectbox('Choose a language', language_options)


# Fetch and display movies
if st.button('Show Movies') and (genre != 'Select a genre' or language != 'Select a language'):

    movies_list = fetch_movies(genre, language)
    movies_list = list(movies_list)
    if not movies_list: 
        st.write('No movies found')
    else:
        for movie in movies_list:
            st.write(movie.title)
else:
    st.write('Please select a genre and language and click on "Show Movies"')