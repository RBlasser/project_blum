import pandas as pd
import sqlite3
import os
from pathlib import Path

def merge_xlsx_to_sqlite():
    """
    Merge all XLSX files from data/imports into a single SQLite database.
    Uses chunked processing to avoid memory issues with large datasets.
    Handles files with different column structures by collecting all unique columns.
    """
    # Define paths
    imports_dir = Path("data/imports")
    output_dir = imports_dir / "merged"
    db_path = output_dir / "merged_data.db"

    # Get all XLSX files
    xlsx_files = sorted(imports_dir.glob("*.xlsx"))

    if not xlsx_files:
        print("No XLSX files found in data/imports")
        return

    print(f"Found {len(xlsx_files)} XLSX files to merge")

    # First pass: collect all unique columns from all files
    print("\nScanning files to identify all columns...")
    all_columns = set()
    file_columns = {}

    for xlsx_file in xlsx_files:
        try:
            # Read just the header to get column names
            df_header = pd.read_excel(xlsx_file, nrows=0)
            cols = list(df_header.columns)
            file_columns[xlsx_file.name] = cols
            all_columns.update(cols)
            print(f"  {xlsx_file.name}: {len(cols)} columns")
        except Exception as e:
            print(f"  Error reading {xlsx_file.name}: {e}")

    # Add source_file column
    all_columns.add('source_file')
    all_columns = sorted(list(all_columns))

    print(f"\nTotal unique columns found: {len(all_columns)}")

    # Create SQLite connection
    conn = sqlite3.connect(db_path)
    table_name = "merged_imports"

    total_rows = 0

    # Second pass: process each file and normalize columns
    print("\nProcessing files...")
    for i, xlsx_file in enumerate(xlsx_files):
        print(f"Processing {xlsx_file.name}...")
        try:
            df = pd.read_excel(xlsx_file)

            # Add source file column
            df['source_file'] = xlsx_file.name

            # Add missing columns with None values
            for col in all_columns:
                if col not in df.columns:
                    df[col] = None

            # Reorder columns to match all_columns
            df = df[all_columns]

            # Write to SQLite in chunks
            if_exists = 'replace' if i == 0 else 'append'
            df.to_sql(table_name, conn, if_exists=if_exists, index=False, chunksize=10000)

            rows_added = len(df)
            total_rows += rows_added
            print(f"  - Added {rows_added:,} rows (Total: {total_rows:,})")

            # Free memory
            del df

        except Exception as e:
            print(f"  - Error processing {xlsx_file.name}: {e}")

    print(f"\nTotal rows merged: {total_rows:,}")
    print(f"Data saved to SQLite database: {db_path}")
    print(f"Table name: {table_name}")
    print(f"\nColumns in merged data ({len(all_columns)}): {all_columns}")

    # Display sample data
    try:
        sample_df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
        print(f"\nFirst few rows:")
        print(sample_df)
    except Exception as e:
        print(f"Could not display sample: {e}")

    conn.close()
    print("\nMerge complete!")

if __name__ == "__main__":
    merge_xlsx_to_sqlite()

