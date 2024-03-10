import streamlit as st
from google.cloud import bigquery
import os
import requests
import pycountry

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\Laurent Sierro\Documents\Clef_Gcloud\kamboo-creek-415115-6445343d2370.json"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/credentials.json"
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"/Users/laurentsierro/Documents/bamboo-creek-415115-6445343d2370.json"


client = bigquery.Client()
api_key = "a4e9b16805164cf6c06689a7bb8da071"
base_url = 'https://api.themoviedb.org/3/'

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
    language_names = []
    for language_code in unique_languages:
        try:
            language_name = pycountry.languages.get(alpha_2=language_code).name
            language_names.append(language_name)
        except AttributeError:
            language_names.append(language_code)
    return sorted(language_names)

def fetch_min_max_years():
    query = """
        SELECT MIN(release_year) AS min_year, MAX(release_year) AS max_year
        FROM `bamboo-creek-415115.movie_rating.movies_description`
    """
    query_job = client.query(query)
    results = query_job.result()
    row = next(results)
    return row['min_year'], row['max_year']

def get_movie_poster_url(tmdb_id, base_url, api_key):

    details_url = f"{base_url}movie/{tmdb_id}?api_key={api_key}"
    
    try:
        response = requests.get(details_url)
        response.raise_for_status()  
        poster_path = response.json().get('poster_path')
        
        if poster_path:
        
            image_base_url = 'https://image.tmdb.org/t/p/w500'  
            
   
            poster_url = f"{image_base_url}{poster_path}"
            return poster_url
        else:
            return "Poster not found."
    except requests.RequestException as e:

        return f"Error fetching poster: {e}"

# Function to fetch movies by genre
def fetch_movies(genre, language, min_avg_rating, title=None, start_year=None, end_year=None):
    # Modified base query to include JOIN and compute average rating
    query = """
        SELECT md.title, md.genres, md.language, md.release_year, md.country, md.tmdbId, AVG(mr.rating) AS average_rating
        FROM `bamboo-creek-415115.movie_rating.movies_description` md
        JOIN `bamboo-creek-415115.movie_rating.movies_rating` mr ON md.movieId = mr.movieId
    """
    conditions = []
    
    if genre != 'Select a genre':
        conditions.append(f"md.genres LIKE '%{genre}%'")
    
    if language != 'Select a language':
        language_code = pycountry.languages.get(name=language).alpha_2
        conditions.append(f"md.language = '{language_code}'")
    if title:
        conditions.append(f"LOWER(md.title) LIKE LOWER('%{title}%')")
    
    if start_year and end_year:
        conditions.append(f"md.release_year BETWEEN {start_year} AND {end_year}")
    
    # Combine WHERE conditions if any
    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)
    
    # Add GROUP BY clause
    query += " GROUP BY md.movieId, md.title, md.genres, md.language, md.release_year, md.country, md.tmdbId"
    
    # Add HAVING clause based on minimum average rating
    if min_avg_rating != 'Select a rating':
        query += f" HAVING AVG(mr.rating) >= {min_avg_rating}"
    
    # Add ORDER BY and LIMIT clauses
    query += " ORDER BY average_rating DESC LIMIT 20"
    
    print("Final Query:", query)
    
    query_job = client.query(query)
    results = query_job.result()
    return results


# Streamlit interface
def main():
    st.title('Movie Finder')

    # Create two columns for the first four fields
    col1, col2 = st.columns(2)

    # Dropdown to select genre
    genre_options = ['Select a genre'] + fetch_genres()
    genre_options.remove('(no genres listed)')
    genre = col1.selectbox('Choose a genre', genre_options, index=0)

    language_options = ['Select a language'] + fetch_languages()
    language = col1.selectbox('Choose a language', language_options)

    title = col2.text_input('Enter a movie title')
    min_avg_rating = col2.slider('Choose a minimum average rating (0-5)', 0.0, 5.0, 0.0, 0.1)

   

    # Full-width slider for release year range
    min_year, max_year = fetch_min_max_years()
    start_year, end_year = st.slider('Select a release year range', min_year, max_year, (min_year, max_year))

    # Fetch and display movies
    if st.button('Show Movies') and (genre != 'Select a genre' or language != 'Select a language' or min_avg_rating or title or start_year <= end_year):
        movies_list = fetch_movies(genre, language, min_avg_rating, title, start_year, end_year)
        movies_list = list(movies_list)
        if not movies_list:
            st.write('No movies found')
        else:
            for movie in movies_list:
                with st.expander(f"**{movie.title}**"):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        try:
                            st.image(get_movie_poster_url(movie.tmdbId, base_url, api_key), width=150)
                        except:
                            st.error("Poster not found.")
                    with col2:
                        genres = movie.genres.replace('|', ', ')
                        st.markdown(f"**Genres:** {genres}")
                        language_name = pycountry.languages.get(alpha_2=movie.language).name
                        st.markdown(f"**Language:** {language_name}")
                        st.markdown(f"**Release Year:** {movie.release_year}")
                        st.markdown(f"**Country:** {movie.country}")
                        st.markdown(f"**Average Rating:** {round(movie.average_rating, 1)}")
    else:
        st.write('Please select a genre, language, and minimum average rating, enter a movie title, and specify a valid release date range, then click on "Show Movies"')

if __name__ == "__main__":
    main()