from auth import load_users, save_users

def add_to_watchlist(username, movie_title): #kto i jaki film 
    users = load_users()
    if movie_title not in users[username]["watchlist"]: # sprawdza czy nie ma juz w watchliscie 
        users[username]["watchlist"].append(movie_title)
        save_users(users)
        return True
    return False

def remove_from_watchlist(username, movie_title):
    users = load_users()
    if movie_title in users[username]["watchlist"]:
        users[username]["watchlist"].remove(movie_title)
        save_users(users)
        return True
    return False

def get_watchlist(username):
    users = load_users()
    return users[username]["watchlist"]