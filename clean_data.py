"""
Reel Insights – TMDB dataset cleaning
Run from the folder containing the six original CSV files:
    python clean_data.py

Outputs are written to ./cleaned_data/ and originals are not modified.
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "cleaned_data"
OUTPUT_DIR.mkdir(exist_ok=True)

FILES = {
    "movies": "movies.csv",
    "movie_keywords": "movie_keywords.csv",
    "movie_genres": "movie_genres.csv",
    "genres": "genres.csv",
    "crew": "crew.csv",
    "cast": "cast.csv",
}

def clean_dataset(name, df):
    # Trim leading/trailing whitespace in text fields.
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].map(lambda value: value.strip() if isinstance(value, str) else value)

    # Remove only exact duplicate rows. Do not drop records just because a field is missing.
    df = df.drop_duplicates().reset_index(drop=True)

    if name == "movies":
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce").dt.strftime("%Y-%m-%d")
        for col in ["movie_id", "runtime", "vote_count"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
        for col in ["budget", "revenue", "popularity", "vote_average"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    elif name in {"movie_keywords", "movie_genres"}:
        for col in df.select_dtypes(include=["number"]).columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
    elif name == "genres":
        df["genre_id"] = pd.to_numeric(df["genre_id"], errors="coerce").round().astype("Int64")
    elif name == "crew":
        for col in ["crew_row_id", "movie_id", "person_id"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")
    elif name == "cast":
        for col in ["cast_row_id", "movie_id", "person_id", "cast_order"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").round().astype("Int64")

    return df

def main():
    report = []
    for name, filename in FILES.items():
        source = BASE_DIR / filename
        if not source.exists():
            raise FileNotFoundError(f"Missing input file: {source}")
        raw = pd.read_csv(source)
        before_rows = len(raw)
        before_duplicates = int(raw.duplicated().sum())
        before_missing = int(raw.isna().sum().sum())
        cleaned = clean_dataset(name, raw.copy())
        cleaned.to_csv(OUTPUT_DIR / f"{name}_clean.csv", index=False)
        report.append({
            "dataset": name,
            "rows_before": before_rows,
            "exact_duplicates_removed": before_duplicates,
            "rows_after": len(cleaned),
            "columns": len(cleaned.columns),
            "missing_cells_before": before_missing,
            "missing_cells_after": int(cleaned.isna().sum().sum()),
        })
        print(f"{name}: {before_rows} -> {len(cleaned)} rows; removed {before_duplicates} exact duplicate rows")

    pd.DataFrame(report).to_csv(OUTPUT_DIR / "cleaning_report.csv", index=False)
    print(f"\nDone. Cleaned files and report saved in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
