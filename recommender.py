from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def recommend_similar_movies(movies_df, watchlist_titles, limit=10):
    """
    Zwraca DataFrame z filmami podobnymi do seed_title i filmow z watchlisty.

     cosine similarity w skrocie:
    - kazdy film zamieniamy na wektor liczb (TF-IDF z tekstu: gatunki + opis + rok)
    - cosine similarity mierzy kat miedzy dwoma wektorami
    - kat = 0  →  filmy identyczne  →  similarity = 1.0
    - kat = 90 →  filmy zupelnie rozne →  similarity = 0.0
    - im wyzszy wynik, tym bardziej podobne filmy
    """

    if "title" not in movies_df.columns:
        return movies_df.head(0)  # zwraca pusty DataFrame jesli brak kolumny title

    working = movies_df.copy()

    #  1: dla kazdego filmu sklejamy tekst z gatunkow + opisu + roku
    # to bedzie "dokument" ktory TF-IDF zamieni na wektor
    working["text_source"] = (
        working["genres"].fillna("") + " " +
        working["overview"].fillna("") + " " +
        working["release_date"].str[:4].fillna("")  # tylko rok, np. "2010"
    )

    # 2: TF-IDF — zamienia teksty na macierz liczb
    # TF = jak czesto slowo wystepuje w danym filmie
    # IDF = jak rzadkie jest to slowo w calej bazie (rzadsze = wazniejsze)
    # stop_words="english" ignoruje slowa typu "the", "a", "is" bo nic nie wnosz
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(working["text_source"])

    # 3: obliczamy podobienstwo miedzy kazdym filmem a kazdym innym
    # wynikiem jest macierz NxN gdzie similarity_matrix[i][j] = podobienstwo filmu i do j
    similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    #  4: slownik title → numer wiersza (index) w macierzy
    title_to_index = {title: idx for idx, title in enumerate(working["title"])}

    #  5: zbieramy "punkty startowe" — film wybrany + filmy z watchlisty
    seed_titles = []
    for title in (watchlist_titles or []):
        if title in title_to_index and title not in seed_titles:
            seed_titles.append(title)

    if not seed_titles:
        return working.head(0)  # brak punktow startowych — zwroc pusty DataFrame

    #  6: dla kazdego seed_title bierzemy wiersz z macierzy podobienstwa
    # potem usredniamy — dostajemy jeden wektor z "przecietnym profilem" watchlisty
    seed_indexes = [title_to_index[t] for t in seed_titles]
    mean_scores = similarity_matrix[seed_indexes].mean(axis=0)
    # mean(axis=0) usrednia wiersze kolumna po kolumnie

    #  7: sortujemy wszystkie filmy od najbardziej do najmniej podobnego
    ranked_indexes = mean_scores.argsort()[::-1]
    # argsort() zwraca indeksy od najmniejszego, [::-1] odwraca na malejace

    #  8: wykluczamy seed filmy z wynikow (nie polecamy tego co juz masz)
    excluded_indexes = set(seed_indexes)

    candidate_indexes = []
    for idx in ranked_indexes:
        if idx not in excluded_indexes:
            candidate_indexes.append(idx)
        if len(candidate_indexes) == limit:
            break

    #  9: zwracamy wiersze DataFrame dla wybranych indeksow
    results = working.iloc[candidate_indexes]
    return results