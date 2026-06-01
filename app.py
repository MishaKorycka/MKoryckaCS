import streamlit as st
import pandas as pd # biblioteka do pracy z danymi w tabelach uzywam jej do wczytania movies csv. I chose it because it is the most popluar one and it is beginner freindly 
import ast # changes the text from movies into python list so that I can work with it (advised by AI)
from pathlib import Path # umożliwia znajdowanie plików niezależnie od komputera na którym uruchamiamy aplikację
from auth import hash_password, load_users, save_users
from watchlist_manager import add_to_watchlist, get_watchlist


st.set_page_config(page_title="Movie Recommender", layout="wide")

DATA_PATH = Path(__file__).parent / "movies.csv" ## ścieżka do pliku z filmami



        
@st.cache_data #dzieki temu streamlit zapamietuje dane zamiast wczytywac od nowa co by zajmowala dlugo
def load_data():
    df = pd.read_csv(DATA_PATH) # czyta tabele i zmienia na dataframe ktora mozemy filtrowac 
    
    def extract_genres(genre_str): 
        try:
            genres = ast.literal_eval(genre_str) # zmienia tekst na liste pythona
            return [g["name"] for g in genres] #wyciaga tylko nazwy gatonkow 
        except Exception: # jesli cokolwiek pojdzie na tak to zwraca pusta liste zamiast sie psuc 
            return []
    
    df["genre_list"] = df["genres"].apply(extract_genres)  #tworzy nową kolumnę z listami gatunków dla każdego filmu
    df["primary_genre"] = df["genre_list"].str[0] # extracts the primary genre  bierze pierwszy genre 
    df = df.dropna(subset=["title", "vote_average", "year", "runtime", "primary_genre"])  # usuwa jak czegos brakuje 
    df = df.drop_duplicates(subset=["title"]) #usuwa duplikaty 
    df = df.reset_index(drop=True) #generuje index dla nowego df, usuwa stary 
    return df
df = load_data()

# Ladowanie danych i pamiec aplikacji 
#Streamlit odświeża cały kod za każdym razem gdy coś klikniesz. 
# Bez tego za każdym kliknięciem logged_in resetowałoby się i użytkownik byłby automatycznie wylogowany
if "logged_in" not in st.session_state: #specjalna pamięć Streamlita która przeżywa odświeżenia strony
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None

# side bar 
with st.sidebar:
    st.title("Account")
    if st.session_state.logged_in: #sprawdza czy ktos jest zalogowany 
        st.success(f"Logged in as **{st.session_state.username}**") # f string pozwala wstawic zmienną w srodek tekstu w tym przypadku nazwe uzytkownika . ** pogrubienie tekstu 
        if st.button("Log out"): #wylogowuje 
            st.session_state.logged_in = False # ustawienia poczatkowe logg false i username none
            st.session_state.username = None
            st.rerun() #odśnwieza strone automatycznie 
    else:
        tab_login, tab_register = st.tabs(["Login", "Register"])
#tworzy dwie zakładki bo tak było bardziej przyjrzyscie 
# REJESTRACJA - formlarz rejestracji, hashuje haslo, sprawdza czy username juz nie istnieje 
        with tab_register:
            reg_username = st.text_input("Choose a username", key="reg_user") #unikalny identyfikator ktory jest potrzebny innaczej streamlit myli username w register i w loginie 
            reg_password = st.text_input("Choose a password", type="password", key="reg_pass") #ukrywa hasło jako kropki 
            if st.button("Register"): 
                if reg_username and reg_password: # sorawdza czy ktos wgl wpisal cos w pole jak nie to kaze mu uzupelnic 
                    users = load_users()
                    if reg_username in users:
                        st.error("Username already exists.")
                    else:
                        users[reg_username] = { #nazwa uzytkownika 
                            "password_hash": hash_password(reg_password), # hashuje haslo przed zapisaniem 
                            "watchlist": [] # pusta lista gotowa na dodawanie filmow 
                        }
                        save_users(users) # zapisuje w userach 
                        st.success("Account created successfully!")
                else:
                    st.warning("Please fill in both fields.")
 #LOGOWANIE                
        with tab_login:
            login_username = st.text_input("Username", key="login_user") 
            login_password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if login_username and login_password: # sprawdza czy pola sa wypelnione 
                    users = load_users()
                    if login_username not in users: 
                        st.error("Username not found.")
                    elif users[login_username]["password_hash"] != hash_password(login_password): # sprawdza czy zgadzaja sie hasla 
                        st.error("Invalid password.")
                    else:
                        st.session_state.logged_in = True
                        st.session_state.username = login_username
                        st.success("Logged in successfully!")
                        st.rerun()
                else:
                    st.warning("Please fill in both fields.")
 
# Interface 

st.title("MOVIE RECOMMENDER")
st.write("Choose your preferences and find the ideal movie")
tab_movies, tab_watchlist = st.tabs(["Matching Movies", "My Watchlist"])

with tab_movies:
    all_genres = sorted(df["primary_genre"].unique()) # w dropdown ustawia alfabetycznie i usuwa powtorzenia 
    
    col1, col2, col3, col4 = st.columns(4) # tworzy 4 kolumny 
    with col1:
        selected_genre = st.selectbox("Genre", ["Any"] + all_genres) # box z gatunkami 
    with col2:
        min_rating = st.slider("Minimum rating", 0.0, 10.0, 0.0, step=0.5) #co 0.5 domyslny 0 
    with col3:
        min_year = st.slider("Year (from)", 1950, 2024, 2000)
    with col4:
        max_length = st.slider("Max length (mins)", 30, 300, 120, step=10) # co 10
    
    st.subheader("Matching Movies")


    st.dataframe(
        df[["title", "vote_average", "primary_genre", "year", "runtime"]].head(30).rename(columns={
            "title": "Title",
            "vote_average": "Rating",
            "primary_genre": "Genre",
            "year": "Year",
            "runtime": "Runtime (min)"
        }),
        use_container_width=True,
        hide_index=True
    )
    if st.session_state.logged_in: # sprawdzamy czy ktos jest zalogowany 
        movie_to_add = st.selectbox("Select movie to add", df["title"].head(30).tolist(), key="add_movie") # tolist potrzebne bo selectbox nie przyjmuje formatu pandas, tylko zwykłą listę
        if st.button("Add to watchlist"):
            if add_to_watchlist(st.session_state.username, movie_to_add):
                st.success(f"'{movie_to_add}' added to watchlist!")
            else:
                st.warning("This movie is already in your watchlist.")
    else:
        st.info("Log in to save movies to your watchlist.")
    #watchlista 
    with tab_watchlist:
        if not st.session_state.logged_in: 
            st.info("Please log in to view your watchlist.")
        else:
            st.subheader("My Watchlist") 
            watchlist = get_watchlist(st.session_state.username) #Wywołuje funkcję z watchlist_manager.py 
            #która otwiera users.json i zwraca listę filmów dla zalogowanego użytkownika.
            if not watchlist:
                st.info("Your watchlist is empty. Add movies to see them here!")
            else:
                st.dataframe( # pokazuje kolmne z filmami # isin sprawdza czy jest w watchliscie i wyswietla
                    df[df["title"].isin(watchlist)][["title", "vote_average", "primary_genre", "year", "runtime"]].rename(columns={
                        "title": "Title",
                        "vote_average": "Rating",
                        "primary_genre": "Genre",
                        "year": "Year",
                        "runtime": "Runtime (min)"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
