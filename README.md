# Reel Insights: An End-to-End Exploratory Data Analysis of the Global Movie Industry (TMDB)

## Project Overview

Reel Insights is a data analytics project that explores the global movie industry using TMDB movie data. It uses Python, Pandas, SQL, data visualization, and Streamlit to investigate movie performance, genres, ratings, budgets, revenue, actors, directors, and keywords.

## Objectives

- Clean and validate six relational movie datasets.
- Store and analyze movie data using a SQL database.
- Answer 10 business questions using SQL.
- Perform 10 exploratory analyses using Pandas.
- Build visualizations to identify trends and relationships.
- Develop a Streamlit dashboard for interactive exploration.

## Tools and Technologies

- Python
- Pandas and NumPy
- SQL and TiDB Cloud
- Matplotlib, Seaborn, and Plotly
- Streamlit
- Jupyter Notebook
- VS Code

## Project Files

- `01_data_cleaning.ipynb` — data inspection, cleaning, and database loading.
- `02_sql_analysis.ipynb` — SQL-based analysis questions.
- `03_pandas_analysis.ipynb` — Pandas-based exploratory analysis.
- `04_visualization.ipynb` — charts and visualization insights.
- `app.py` — interactive Streamlit dashboard.
- `.env` — database connection settings. Do not publish credentials.

## Key Analysis Areas

1. Movie budgets, revenue, profit, and ROI.
2. Movie production trends by release year.
3. Genre-level ratings, popularity, and revenue.
4. Actor and director contributions.
5. Keyword frequency and movie metadata.
6. Relationships between popularity, ratings, and vote counts.

## Top 5 Insights

1. **Revenue Performance:** The SQL analysis identifies the highest-grossing movies and their associated genres.

2. **Investment Performance:** The Pandas analysis calculates profit and ROI for movies with valid budget and revenue data.

3. **Genre Trends:** The analysis compares average revenue and ratings across genres.

4. **Production Trends:** The analysis examines yearly movie releases to identify production trends.

5. **Audience Engagement:** The analysis examines the relationship between movie popularity and vote counts, including unusual observations.

## Recommendations

- Compare budget and revenue together when assessing movie performance.
- Treat missing and zero financial values carefully during profitability and ROI calculations.
- Consider vote counts alongside average ratings when interpreting audience response.
- Use genre and release-year trends to guide further analysis.
- Validate findings against the actual dataset before making business decisions.

## How to Run the Dashboard

1. Open the project folder in VS Code.
2. Activate the Python environment containing the required packages.
3. Ensure the `.env` file contains the appropriate database connection settings.
4. Run the application:

```bash
streamlit run app.py
```

5. Open the local URL displayed in the terminal.

## Data

The project uses six related CSV datasets: movies, genres, movie-genres relationships, cast, crew, and movie keywords. Cleaned versions are included in the project folder.

## Note

The final numerical findings and recommendations should be verified against the completed SQL queries, Pandas outputs, and visualizations. Database credentials and other secrets must not be committed to a public repository.