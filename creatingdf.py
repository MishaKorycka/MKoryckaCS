import pandas as pd 

df=pd.read_csv("tmdb_5000_movies.csv")
df.to_csv("movies.csv", index=False)







