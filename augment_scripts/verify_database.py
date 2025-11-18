import sqlite3
import pandas as pd
from pathlib import Path

def verify_database():
    """
    Verify the merged SQLite database.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Database found at: {db_path}")
    print(f"Database size: {db_path.stat().st_size / (1024**2):.2f} MB")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    
    # Get table info
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\nTables in database: {[t[0] for t in tables]}")
    
    # Get row count
    cursor.execute("SELECT COUNT(*) FROM merged_imports;")
    row_count = cursor.fetchone()[0]
    print(f"\nTotal rows in merged_imports: {row_count:,}")
    
    # Get column info
    cursor.execute("PRAGMA table_info(merged_imports);")
    columns = cursor.fetchall()
    print(f"\nColumns ({len(columns)}):")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Get sample data
    print("\nSample data (first 5 rows):")
    df = pd.read_sql("SELECT * FROM merged_imports LIMIT 5", conn)
    print(df)
    
    # Get count by source file
    print("\nRows by source file:")
    df_counts = pd.read_sql("""
        SELECT source_file, COUNT(*) as row_count 
        FROM merged_imports 
        GROUP BY source_file 
        ORDER BY source_file
    """, conn)
    print(df_counts)
    
    conn.close()
    print("\nVerification complete!")

if __name__ == "__main__":
    verify_database()

