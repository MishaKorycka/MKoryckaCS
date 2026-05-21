import streamlit as st
import pandas as pd
import ast
from pathlib import Path

st.set_page_config(page_title="Movie Recommender", layout="wide")


DATA_PATH = Path(__file__).parent / "movies.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    
    def extract_genres(genre_str):
        try:
            genres = ast.literal_eval(genre_str)
            return [g["name"] for g in genres]
        except Exception:
            return []
    
    df["genre_list"] = df["genres"].apply(extract_genres)
    df["primary_genre"] = df["genre_list"].apply(lambda g: g[0] if g else "Unknown")
    df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year
    df = df.dropna(subset=["title", "vote_average", "year"])
    df = df.drop_duplicates(subset=["title"])
    df = df.reset_index(drop=True)
    return df
df = load_data()


st.title("movie recommender")
st.write("Chose your preferances and find the ideal movie")