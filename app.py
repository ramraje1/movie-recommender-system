import streamlit as st
import pickle
import pandas as pd
import requests
import difflib
import gzip
import gdown
import os
# --- Function to fetch poster using OMDb API ---
def fetch_poster(movie_title):
    api_key = st.secrets["OMDB_API_KEY"]   
    url = f"http://www.omdbapi.com/?t={movie_title}&apikey={api_key}"
    data = requests.get(url).json()

    if 'Poster' in data and data['Poster'] != 'N/A':
        return data['Poster']
    else:
        return "https://via.placeholder.com/300x450.png?text=No+Poster+Available"

# --- Function to recommend similar movies ---
def recommend(movie):
    movie = movie.strip().title()
    all_titles = movies['title'].tolist()
    match = difflib.get_close_matches(movie, all_titles, n=1, cutoff=0.6)

    if not match:
        return ["Movie not found in database. Please try another title."], []

    movie_name = match[0]
    index = movies[movies['title'] == movie_name].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    for i in distances:
        movie_title = movies.iloc[i[0]].title
        recommended_movies.append(movie_title)
        recommended_posters.append(fetch_poster(movie_title))
    return recommended_movies, recommended_posters

# --- Load saved data ---
movies = pickle.load(open('movie.pkl', 'rb'))
file_id = "1vLv2eS4-pPzSOLubzs39XGSMUgbiFSvc"
url = f"https://drive.google.com/uc?id={file_id}"
output = "similaritiy.pkl.gz"

if not os.path.exists(output):
    gdown.download(url, output, quiet=False)
with gzip.open(output, 'rb') as f:
    similarity = pickle.load(f)


# --- Streamlit UI ---
st.title("🎥 Movie Recommender System")
selected_movie = st.selectbox("Select or type a movie name", movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(selected_movie)

    if "Movie not found" in names[0]:
        st.error(names[0])
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]
        for i in range(5):
            with cols[i]:
                st.text(names[i])
                st.image(posters[i])

