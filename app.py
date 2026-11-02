

import streamlit as st
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Reel Insights TMDB",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Reel Insights — TMDB Dashboard")

host = os.getenv("TIDB_HOST")
port = os.getenv("TIDB_PORT", "4000")
user = os.getenv("TIDB_USER")
password = os.getenv("TIDB_PASSWORD")
database = os.getenv("TIDB_DATABASE")

if not all([host, user, password, database]):
    st.error("Database settings missing. Please configure your .env file.")
    st.stop()


from urllib.parse import quote_plus


from urllib.parse import quote_plus

try:
    engine = create_engine(
        f"mysql+pymysql://{quote_plus(user)}:"
        f"{quote_plus(password)}@{host}:{port}/{database}",
        connect_args={"ssl": {}}
    )

    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES"))
        tables = [row[0] for row in result.fetchall()]

    st.success("Connected to TiDB Cloud successfully!")
    st.write("Database tables:", tables)

except Exception as e:
    st.error(f"Database connection failed: {e}")

st.subheader("🎬 Movie Dashboard")

with engine.connect() as conn:
    movies = pd.read_sql(
        text("""
            SELECT movie_id,title, release_date, budget, revenue,
                   popularity, vote_average, vote_count,
                   original_language
            FROM movies
        """),
        conn
    )
st.sidebar.header("🎬 Movie Filters")

movies["release_date"] = pd.to_datetime(
    movies["release_date"], errors="coerce"
)

movies["release_year"] = movies["release_date"].dt.year

years = sorted(
    movies["release_year"].dropna().astype(int).unique()
)

selected_years = st.sidebar.multiselect(
    "Select Release Year",
    years,
    default=years
)

languages = sorted(
    movies["original_language"].dropna().unique()
)

selected_languages = st.sidebar.multiselect(
    "Select Language",
    languages,
    default=languages
)
genre_options = ["All"]

with engine.connect() as conn:
    genres_list = pd.read_sql(
        text("SELECT genre_name FROM genres ORDER BY genre_name"),
        conn
    )

genre_options += genres_list["genre_name"].dropna().tolist()

selected_genres = st.sidebar.multiselect(
    "Select Genre",
    genre_options,
    default=["All"]
)
min_rating = st.sidebar.slider(
    "Minimum Rating",
    min_value=0.0,
    max_value=10.0,
    value=0.0,
    step=0.5
)

filtered_movies = movies[
    movies["release_year"].isin(selected_years)
    & movies["original_language"].isin(selected_languages)
    & (movies["vote_average"] >= min_rating)
]

if "All" not in selected_genres and selected_genres:
    with engine.connect() as conn:
        genre_movies = pd.read_sql(
            text("""
                SELECT DISTINCT mg.movie_id
                FROM movie_genres mg
                JOIN genres g ON mg.genre_id = g.genre_id
                WHERE g.genre_name IN :genre_names
            """),
            conn,
            params={"genre_names": tuple(selected_genres)}
        )

    filtered_movies = filtered_movies[
        filtered_movies["movie_id"].isin(genre_movies["movie_id"])
    ]

genre_count = 0
actor_count = 0

if not filtered_movies.empty:
    with engine.connect() as conn:
        genre_count = conn.execute(
            text("""
                SELECT COUNT(DISTINCT mg.genre_id)
                FROM movie_genres mg
                WHERE mg.movie_id IN :movie_ids
            """),
            {"movie_ids": tuple(filtered_movies["movie_id"].tolist())}
        ).scalar() or 0

        actor_count = conn.execute(
            text("""
                SELECT COUNT(DISTINCT c.actor_name)
                FROM cast_clean c
                WHERE c.movie_id IN :movie_ids
            """),
            {"movie_ids": tuple(filtered_movies["movie_id"].tolist())}
        ).scalar() or 0

col1, col2, col3,col4 = st.columns(4)

col1.metric("Total Movies", f"{len(filtered_movies):,}")
col2.metric(
    "Average Rating",
    f"{filtered_movies['vote_average'].mean():.2f}/10"
)
col3.metric("Total Genres", f"{genre_count:,}")
col4.metric("Total Actors", f"{actor_count:,}")

st.subheader("Top 10 Movies by Revenue")
top_movies = filtered_movies.nlargest(10, "revenue")
st.bar_chart(top_movies.set_index("title")["revenue"])

st.subheader("🎭 Genre Distribution")

with engine.connect() as conn:
    genre_data = pd.read_sql(
        text("""
            SELECT g.genre_name, COUNT(DISTINCT mg.movie_id) AS movie_count
            FROM movie_genres mg
            JOIN genres g ON mg.genre_id = g.genre_id
            JOIN movies m ON mg.movie_id = m.movie_id
            GROUP BY g.genre_name
            ORDER BY movie_count DESC
        """),
        conn
    )

st.bar_chart(
    genre_data.set_index("genre_name")["movie_count"]
)
st.subheader("💰 Budget vs Revenue")

scatter_data = filtered_movies[
    (filtered_movies["budget"] > 0) &
    (filtered_movies["revenue"] > 0)
]

st.scatter_chart(
    scatter_data,
    x="budget",
    y="revenue"
)
st.subheader("Movie Data")
st.dataframe(filtered_movies.head(20), use_container_width=True)

st.divider()

st.header("🔎 Query Explorer")

saved_queries = {
    "Q1. Action Movies Released After 2015": """
        SELECT DISTINCT m.title, m.release_date
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        WHERE g.genre_name = 'Action'
          AND m.release_date >= '2016-01-01'
        ORDER BY m.release_date
    """,

    "Q2. Top 10 Highest-Grossing Movies with Genres": """
        SELECT m.title, m.revenue,
               GROUP_CONCAT(DISTINCT g.genre_name) AS genres
        FROM movies m
        LEFT JOIN movie_genres mg ON m.movie_id = mg.movie_id
        LEFT JOIN genres g ON mg.genre_id = g.genre_id
        WHERE m.revenue > 0
        GROUP BY m.movie_id, m.title, m.revenue
        ORDER BY m.revenue DESC
        LIMIT 10
    """,

    "Q3. Average Budget and Revenue by Genre": """
        SELECT g.genre_name,
               AVG(NULLIF(m.budget, 0)) AS average_budget,
               AVG(NULLIF(m.revenue, 0)) AS average_revenue
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON mg.genre_id = g.genre_id
        GROUP BY g.genre_id, g.genre_name
        ORDER BY average_revenue DESC
    """,

    "Q4. Top 10 Actors by Movie Count": """
        SELECT actor_name, COUNT(DISTINCT movie_id) AS movie_count
        FROM cast_clean
        WHERE actor_name IS NOT NULL
        GROUP BY person_id, actor_name
        ORDER BY movie_count DESC
        LIMIT 10
    """,

    "Q5. Directors with More Than 3 Movies": """
        SELECT person_name AS director_name,
               COUNT(DISTINCT movie_id) AS movie_count
        FROM crew_clean
        WHERE job = 'Director' AND person_name IS NOT NULL
        GROUP BY person_id, person_name
        HAVING COUNT(DISTINCT movie_id) > 3
        ORDER BY movie_count DESC
    """,

    "Q6. Top 10 Most-Used Keywords": """
        SELECT keyword_name, COUNT(DISTINCT movie_id) AS movie_count
        FROM movie_keywords_clean
        WHERE keyword_name IS NOT NULL
        GROUP BY keyword_id, keyword_name
        ORDER BY movie_count DESC
        LIMIT 10
    """,

    "Q7. Above-Average Budget, Below-Average Revenue": """
        SELECT title, budget, revenue
        FROM movies
        WHERE budget > (SELECT AVG(budget) FROM movies WHERE budget > 0)
          AND revenue > 0
          AND revenue < (SELECT AVG(revenue) FROM movies WHERE revenue > 0)
        ORDER BY budget DESC
    """,

    "Q8. Actors in Christopher Nolan Movies": """
        SELECT DISTINCT c.actor_name, m.title AS movie_title
        FROM cast_clean c
        JOIN movies m ON m.movie_id = c.movie_id
        JOIN crew_clean d ON d.movie_id = m.movie_id
        WHERE d.job = 'Director'
          AND LOWER(d.person_name) = 'christopher nolan'
        ORDER BY m.title, c.actor_name
    """,

    "Q9. Highest-Rated Genre (At Least 20 Movies)": """
        SELECT g.genre_name,
               AVG(m.vote_average) AS average_rating,
               COUNT(DISTINCT m.movie_id) AS movie_count
        FROM movies m
        JOIN movie_genres mg ON m.movie_id = mg.movie_id
        JOIN genres g ON g.genre_id = mg.genre_id
        WHERE m.vote_average IS NOT NULL
        GROUP BY g.genre_id, g.genre_name
        HAVING COUNT(DISTINCT m.movie_id) >= 20
        ORDER BY average_rating DESC
        LIMIT 1
    """,

    "Q10. Top 10 Movies with Most Keywords": """
        SELECT m.title, COUNT(DISTINCT k.keyword_id) AS keyword_count
        FROM movies m
        JOIN movie_keywords_clean k ON k.movie_id = m.movie_id
        GROUP BY m.movie_id, m.title
        ORDER BY keyword_count DESC
        LIMIT 10
    """
}
selected_query = st.selectbox(
    "Choose an analysis",
    list(saved_queries.keys())
)

if st.button("Run Query"):
    try:
        with engine.connect() as conn:
            query_result = pd.read_sql(
                text(saved_queries[selected_query]),
                conn
            )

        st.subheader("Query Results")
        st.dataframe(query_result, use_container_width=True)

        numeric_columns = query_result.select_dtypes(
            include="number"
        ).columns.tolist()

        if len(query_result.columns) >= 2 and numeric_columns:
            chart_column = numeric_columns[-1]
            st.subheader("Result Chart")
            st.bar_chart(
                query_result.set_index(query_result.columns[0])[
                    chart_column
                ]
            )

        query_insights = {
    "Q1. Action Movies Released After 2015":
        "This query identifies Action movies released after 2015. "
        "It helps analyze recent Action movie releases.",

    "Q2. Top 10 Highest-Grossing Movies with Genres":
        "This query highlights the 10 movies with the highest box-office "
        "revenue and shows their associated genres.",

    "Q3. Average Budget and Revenue by Genre":
        "This query compares average production budget and revenue "
        "across genres to identify financially strong genres.",

    "Q4. Top 10 Actors by Movie Count":
        "This query identifies the 10 actors who appeared in the "
        "highest number of movies in the dataset.",

    "Q5. Directors with More Than 3 Movies":
        "This query finds directors who have directed more than "
        "three movies and compares their movie counts.",

    "Q6. Top 10 Most-Used Keywords":
        "This query identifies the most frequently used movie "
        "keywords and highlights common themes.",

    "Q7. Above-Average Budget, Below-Average Revenue":
        "This query identifies movies with above-average budgets "
        "but below-average revenue. These movies may indicate "
        "higher financial risk.",

    "Q8. Actors in Christopher Nolan Movies":
        "This query lists actors who appeared in movies directed "
        "by Christopher Nolan.",

    "Q9. Highest-Rated Genre (At Least 20 Movies)":
        "This query identifies the highest-rated genre among "
        "genres containing at least 20 movies.",

    "Q10. Top 10 Movies with Most Keywords":
        "This query identifies the 10 movies associated with "
        "the highest number of keywords."
}

        st.subheader("💡 Query Explanation & Insight")
        st.info(query_insights[selected_query])

    except Exception as e:
        st.error(f"Query failed: {e}")     
