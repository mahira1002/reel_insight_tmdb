import pandas as pd


movies_df = pd.read_csv('movies.csv')
genres_df = pd.read_csv('genres.csv')
cast_df = pd.read_csv('cast.csv')
crew_df = pd.read_csv('crew.csv')
movie_genres_df = pd.read_csv('movie_genres.csv')
movie_keywords_df = pd.read_csv('movie_keywords.csv')

print("files-successfully load !")
print("Movies shape:", movies_df.shape)
print("Genres shape:", genres_df.shape)

print("\n--- ALL DATASET SHAPES ---")

datasets = {
    "Movies": movies_df,
    "Genres": genres_df,
    "Cast": cast_df,
    "Crew": crew_df,
    "Movie Genres": movie_genres_df,
    "Movie Keywords": movie_keywords_df
}

for name, df in datasets.items():
    print(f"\n{name}")
    print("Shape:", df.shape)
    print("Duplicate rows:", df.duplicated().sum())
    print("Missing values:", df.isnull().sum().sum())
    print("Columns:", df.columns.tolist())


print("\n--- DUPLICATE ROW DETAILS ---")

for name, df in datasets.items():
    duplicates = df[df.duplicated()]

    if not duplicates.empty:
        print(f"\n{name}:")
        print(duplicates.head(5))

print("\n--- DATA TYPES CHECK ---")
for name, df in dataframes.items():
    print(f"\n{name}")
    print(df.dtypes)